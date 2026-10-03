"""Aggregate raw per-group results into metrics.json, statistics.json, hypotheses.json and tables.

All numbers reported in the manuscript are read from the files written here.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.statistics.tests import bootstrap_ci, holm, wilcoxon_paired
from src.utils import RESULTS

ROOT = os.path.dirname(RESULTS)
TABLES = os.environ.get("TABLE_DIR", os.path.join(ROOT, "tables"))
os.makedirs(TABLES, exist_ok=True)
PROPOSED = "GC-D"
TASK_LABEL = {
    "mango_season_loso": "Mango: new season (LOSO)",
    "mango_season_forward": "Mango: next season (forward)",
    "mango_instrument": "Mango: new instrument",
    "mango_population": "Mango: new population",
    "ossl_lucas_block": "Soil (LUCAS): new region",
    "ossl_lucas_campaign": "Soil (LUCAS): other campaign",
    "ossl_kssl_to_lucas": "Soil: KSSL → LUCAS library",
    "corn_moisture": "Corn moisture: new instrument",
    "corn_oil": "Corn oil: new instrument",
    "corn_protein": "Corn protein: new instrument",
    "corn_starch": "Corn starch: new instrument",
    "tablets": "Tablets (control / new instrument)",
}
MAIN_TASKS = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population",
              "ossl_lucas_block", "corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
GEN_TASKS = ["ossl_lucas_campaign", "ossl_kssl_to_lucas", "tablets"]


def load_raw(sub="main"):
    files = sorted(glob.glob(os.path.join(RESULTS, sub, "groups_*.csv")))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df[~df.method.isin(["GC-D2", "GC-CQR"])]  # post-hoc methods: analysed in aggregate_extra.py only
    if "error" in df:
        err = df[df["error"].notna()]
        if len(err):
            print(f"WARNING: {len(err)} failed method runs recorded", err[["task", "fold", "method", "alpha", "error"]].head())
        df = df[df["error"].isna()].drop(columns=["error"])
    return df


def per_group(df):
    """Average over seeds -> one row per (task, method, alpha, fold, group)."""
    g = df.groupby(["task", "method", "alpha", "fold", "group"], as_index=False)
    out = g.agg(n=("n", "first"), coverage=("coverage", "mean"), coverage_seed_sd=("coverage", "std"),
                width=("width_mean", "mean"), interval_score=("interval_score", "mean"),
                rmse=("rmse", "mean"), bias=("bias", "mean"), time_s=("time_s", "mean"), n_seeds=("seed", "nunique"))
    return out


def summarize(pg, df):
    rows = []
    for (task, meth, a), d in pg.groupby(["task", "method", "alpha"]):
        nominal = 1 - a
        cov = d.coverage.to_numpy()
        lo, hi = bootstrap_ci(cov, seed=0)
        # seed variability of the group-averaged coverage
        sd_seed = df[(df.task == task) & (df.method == meth) & (df.alpha == a)].groupby("seed").coverage.mean().std()
        isc = d.interval_score.to_numpy()
        rows.append(dict(task=task, method=meth, alpha=a, n_groups=len(d), n_spectra=int(d.n.sum()),
                         coverage=float(cov.mean()), coverage_ci_lo=lo, coverage_ci_hi=hi,
                         coverage_pooled=float(np.average(cov, weights=d.n)),
                         coverage_min=float(cov.min()), coverage_seed_sd=float(sd_seed) if np.isfinite(sd_seed) else 0.0,
                         share_under=float(np.mean(cov < nominal - 0.05)),
                         width=float(d.width.mean()), width_median=float(d.width.median()),
                         interval_score=float(isc.mean()), interval_score_median=float(np.median(isc)),
                         rmse=float(d.rmse.mean()), time_s=float(d.time_s.mean())))
    return pd.DataFrame(rows)


def compare(pg, alpha=0.1):
    out = []
    for task, d in pg[pg.alpha == alpha].groupby("task"):
        piv_is = d.pivot_table(index=["fold", "group"], columns="method", values="interval_score")
        piv_cov = d.pivot_table(index=["fold", "group"], columns="method", values="coverage")
        if PROPOSED not in piv_is:
            continue
        others = [m for m in piv_is.columns if m not in (PROPOSED, "ORACLE", "GC-D2", "GC-CQR")]
        res = []
        for m in others:
            r1 = wilcoxon_paired(piv_is[PROPOSED].values, piv_is[m].values)
            r2 = wilcoxon_paired(np.abs(piv_cov[PROPOSED].values - (1 - alpha)), np.abs(piv_cov[m].values - (1 - alpha)))
            res.append(dict(task=task, comparator=m, n_groups=r1["n_pairs"],
                            IS_median_diff=r1["median_diff"], IS_r_rb=r1["r_rb"], IS_p=r1["p"],
                            covgap_median_diff=r2["median_diff"], covgap_r_rb=r2["r_rb"], covgap_p=r2["p"]))
        r = pd.DataFrame(res)
        r["IS_p_holm"] = holm(r.IS_p.values)
        r["covgap_p_holm"] = holm(r.covgap_p.values)
        out.append(r)
    return pd.concat(out, ignore_index=True)


def hypotheses(summ, comp, folds_info):
    s = summ[summ.alpha == 0.1]
    h = {}
    scp = s[(s.method == "SCP") & s.task.isin(MAIN_TASKS)].set_index("task").coverage
    h["H1"] = dict(statement="SCP group-averaged coverage < 0.85 on at least one shift task",
                   values=scp.round(4).to_dict(), supported=bool((scp < 0.85).any()))
    gc = s[(s.method == PROPOSED) & s.task.isin(MAIN_TASKS)].set_index("task").coverage
    many = [t for t in gc.index if folds_info.get(t, 0) >= 10]
    h["H2"] = dict(statement="GC-D group-averaged coverage in [0.87, 0.95] on every task with >= 10 training groups",
                   tasks_with_ge10_groups=many, values=gc.round(4).to_dict(),
                   supported=bool(all(0.87 <= gc[t] <= 0.95 for t in many)),
                   per_task={t: bool(0.87 <= gc[t] <= 0.95) for t in many})
    c = comp[(comp.comparator == "G-W-A") & comp.task.isin(MAIN_TASKS)]
    h["H3"] = dict(statement="Diagnostic normalisation lowers interval score vs. absolute scores (GC-D vs G-W-A)",
                   per_task={r.task: dict(median_diff=round(r.IS_median_diff, 4), r_rb=round(r.IS_r_rb, 3),
                                          p_holm=float(r.IS_p_holm)) for r in c.itertuples()},
                   n_tasks_lower=int((c.IS_median_diff < 0).sum()),
                   n_tasks_significant_lower=int(((c.IS_median_diff < 0) & (c.IS_p_holm < 0.05)).sum()),
                   n_tasks=int(len(c)))
    return h


def main():
    df = load_raw("main")
    df.to_csv(os.path.join(RESULTS, "raw_results.csv"), index=False)
    pg = per_group(df)
    pg.to_csv(os.path.join(RESULTS, "per_group_results.csv"), index=False)
    summ = summarize(pg, df)
    summ.to_csv(os.path.join(RESULTS, "summary_results.csv"), index=False)
    comp = compare(pg)
    comp.to_csv(os.path.join(RESULTS, "comparisons_alpha0.1.csv"), index=False)
    finfo = {}
    for f in glob.glob(os.path.join(RESULTS, "main", "folds_*_seed0.csv")):
        t = os.path.basename(f)[6:-10]
        fi = pd.read_csv(f)
        finfo[t] = int(fi.n_calib_groups.min())
    hyp = hypotheses(summ, comp, finfo)
    metrics = {t: {m: {str(a): r for a, r in d.set_index("alpha").drop(columns=["task", "method"]).to_dict("index").items()}
                   for m, d in dt.groupby("method")} for t, dt in summ.groupby("task")}
    json.dump(dict(metrics=metrics, min_calibration_groups=finfo), open(os.path.join(RESULTS, "metrics.json"), "w"), indent=1)
    json.dump(dict(comparisons=comp.to_dict("records"), hypotheses=hyp,
                   test="two-sided Wilcoxon signed-rank (exact if <=25 non-zero pairs), unit = held-out group, "
                        "per-group values averaged over seeds; Holm correction across comparators within task; "
                        "effect size = matched-pairs rank-biserial correlation (negative = GC-D lower)"),
              open(os.path.join(RESULTS, "statistics.json"), "w"), indent=1, default=float)
    json.dump(hyp, open(os.path.join(RESULTS, "hypotheses.json"), "w"), indent=1, default=float)
    print(json.dumps(hyp, indent=1, default=float))


if __name__ == "__main__":
    main()
