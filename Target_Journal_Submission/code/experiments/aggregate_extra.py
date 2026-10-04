"""Aggregate post-hoc iteration, robustness, sensitivity and CNN experiments."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.statistics.tests import holm, wilcoxon_paired
from src.utils import RESULTS


def pg_mean(df, keys=("task", "method", "group")):
    # group-level averaging over seeds (fold omitted: mango_population folds differ between seeds)
    return df.groupby(list(keys), as_index=False).agg(coverage=("coverage", "mean"), width=("width_mean", "mean"),
                                                      interval_score=("interval_score", "mean"), n=("n", "first"))


def summarize_table(pg, by):
    return pg.groupby(by, as_index=False).agg(coverage=("coverage", "mean"), coverage_min=("coverage", "min"),
                                              width=("width", "mean"), interval_score=("interval_score", "mean"),
                                              n_groups=("coverage", "size"))


def iteration():
    fs = glob.glob(os.path.join(RESULTS, "iteration1", "groups_*.csv"))
    if not fs:
        return None
    df = pd.concat([pd.read_csv(f) for f in fs])
    if "error" in df:
        df = df[df.error.isna()]
    pg = pg_mean(df)
    summ = summarize_table(pg, ["task", "method"])
    summ.to_csv(os.path.join(RESULTS, "iteration1_summary.csv"), index=False)
    rows = []
    for t, d in pg.groupby("task"):
        P = d.pivot_table(index="group", columns="method", values="interval_score")
        C = d.pivot_table(index="group", columns="method", values="coverage")
        for a, b in [("GC-D2", "GC-D"), ("GC-CQR", "CQR"), ("GC-CQR", "GC-D")]:
            if a in P and b in P:
                r = wilcoxon_paired(P[a].values, P[b].values)
                rc = wilcoxon_paired(np.abs(C[a].values - 0.9), np.abs(C[b].values - 0.9))
                rows.append(dict(task=t, method=a, comparator=b, n_groups=r["n_pairs"], IS_median_diff=r["median_diff"],
                                 IS_r_rb=r["r_rb"], IS_p=r["p"], covgap_median_diff=rc["median_diff"], covgap_p=rc["p"]))
    comp = pd.DataFrame(rows)
    comp["IS_p_holm"] = np.nan
    for (m, c), idx in comp.groupby(["method", "comparator"]).groups.items():
        comp.loc[idx, "IS_p_holm"] = holm(comp.loc[idx, "IS_p"].values)  # Holm across tasks per contrast
    comp.to_csv(os.path.join(RESULTS, "iteration1_comparisons.csv"), index=False)
    return dict(summary=summ.to_dict("records"), comparisons=comp.to_dict("records"))


def robustness():
    rd = os.path.join(RESULTS, "robustness")
    out = {}
    g = glob.glob(os.path.join(rd, "groups_*_K*_rep*.csv"))
    if g:
        d = pd.concat([pd.read_csv(f) for f in g])
        d = d[d.get("error", pd.Series(np.nan, index=d.index)).isna()] if "error" in d else d
        s = d.groupby(["task", "method", "K", "rep"]).agg(coverage=("coverage", "mean"), width=("width_mean", "mean"),
                                                         finite=("finite_frac", "mean")).reset_index()
        s = s.groupby(["task", "method", "K"]).agg(coverage=("coverage", "mean"), coverage_sd=("coverage", "std"),
                                                    width=("width", "mean"), finite=("finite", "mean")).reset_index()
        s.to_csv(os.path.join(RESULTS, "robustness_groups_summary.csv"), index=False); out["groups"] = s.to_dict("records")
    z = glob.glob(os.path.join(rd, "size_frac*.csv"))
    if z:
        d = pd.concat([pd.read_csv(f) for f in z])
        s = d.groupby(["method", "frac", "rep"]).agg(coverage=("coverage", "mean"), IS=("interval_score", "mean")).reset_index()
        s = s.groupby(["method", "frac"]).agg(coverage=("coverage", "mean"), coverage_sd=("coverage", "std"),
                                              interval_score=("IS", "mean")).reset_index()
        s.to_csv(os.path.join(RESULTS, "robustness_size_summary.csv"), index=False); out["size"] = s.to_dict("records")
    p = glob.glob(os.path.join(rd, "perturb_*.csv"))
    if p:
        d = pd.concat([pd.read_csv(f) for f in p])
        s = d.groupby(["perturbation", "level", "method"]).agg(coverage=("coverage", "mean"), width=("width_mean", "mean"),
                                                               interval_score=("interval_score", "mean"), rmse=("rmse", "mean")).reset_index()
        s.to_csv(os.path.join(RESULTS, "robustness_perturb_summary.csv"), index=False); out["perturb"] = s.to_dict("records")
    sv = glob.glob(os.path.join(rd, "sens_*.csv"))
    if sv:
        d = pd.concat([pd.read_csv(f) for f in sv])
        s = d.groupby(["task", "variant", "method"]).agg(coverage=("coverage", "mean"), width=("width_mean", "mean"),
                                                         interval_score=("interval_score", "mean"), A=("A", "mean")).reset_index()
        s.to_csv(os.path.join(RESULTS, "sensitivity_summary.csv"), index=False); out["sensitivity"] = s.to_dict("records")
    c = glob.glob(os.path.join(RESULTS, "cnn", "groups_cnn_*.csv"))
    if c:
        d = pd.concat([pd.read_csv(f) for f in c])
        pg = d.groupby(["method", "fold"]).agg(coverage=("coverage", "mean"), width=("width_mean", "mean"),
                                               interval_score=("interval_score", "mean"), rmse=("rmse", "mean")).reset_index()
        s = pg.groupby("method").agg(coverage=("coverage", "mean"), coverage_min=("coverage", "min"), width=("width", "mean"),
                                     interval_score=("interval_score", "mean"), rmse=("rmse", "mean"),
                                     n_seasons=("fold", "nunique")).reset_index()
        s["n_seeds"] = d.seed.nunique()
        s.to_csv(os.path.join(RESULTS, "cnn_summary.csv"), index=False); out["cnn"] = s.to_dict("records")
        pg.to_csv(os.path.join(RESULTS, "cnn_per_season.csv"), index=False)
    return out


def wcp_clip():
    fs = glob.glob(os.path.join(RESULTS, "wcp_clip", "groups_*.csv"))
    if not fs:
        return None
    d = pd.concat([pd.read_csv(f) for f in fs])
    pg = d.groupby(["task", "method", "group"], as_index=False).agg(coverage=("coverage", "mean"),
                                                                           width=("width_mean", "mean"),
                                                                           interval_score=("interval_score", "mean"),
                                                                           finite=("finite_frac", "mean"))
    s = pg.groupby(["task", "method"], as_index=False).agg(coverage=("coverage", "mean"), width_median=("width", "median"),
                                                            interval_score=("interval_score", "mean"),
                                                            finite_frac=("finite", "mean"), n_groups=("coverage", "size"))
    s["n_seeds"] = d.seed.nunique()
    s.to_csv(os.path.join(RESULTS, "wcp_clip_summary.csv"), index=False)
    return s.to_dict("records")


def cultivar():
    fs = glob.glob(os.path.join(RESULTS, "cultivar", "groups_*.csv"))
    if not fs:
        return None
    d = pd.concat([pd.read_csv(f) for f in fs])
    pg = d.groupby(["method", "group"], as_index=False).agg(coverage=("coverage", "mean"), width=("width_mean", "mean"),
                                                            interval_score=("interval_score", "mean"), rmse=("rmse", "mean"),
                                                            bias=("bias", "mean"))
    pg.to_csv(os.path.join(RESULTS, "cultivar_per_group.csv"), index=False)
    s = pg.groupby("method", as_index=False).agg(coverage=("coverage", "mean"), coverage_min=("coverage", "min"),
                                                 width=("width", "mean"), interval_score=("interval_score", "mean"),
                                                 n_cultivars=("group", "nunique"))
    s["n_seeds"] = d.seed.nunique()
    rows = []
    P = pg.pivot(index="group", columns="method", values="interval_score")
    Cv = pg.pivot(index="group", columns="method", values="coverage")
    for m in [c for c in P.columns if c not in ("GC-D", "ORACLE")]:
        r = wilcoxon_paired(P["GC-D"].values, P[m].values)
        rc = wilcoxon_paired(np.abs(Cv["GC-D"].values - 0.9), np.abs(Cv[m].values - 0.9))
        rows.append(dict(comparator=m, n=r["n_pairs"], IS_median_diff=r["median_diff"], IS_r_rb=r["r_rb"], IS_p=r["p"],
                         covgap_median_diff=rc["median_diff"], covgap_p=rc["p"]))
    c = pd.DataFrame(rows); c["IS_p_holm"] = holm(c.IS_p.values); c["covgap_p_holm"] = holm(c.covgap_p.values)
    s.to_csv(os.path.join(RESULTS, "cultivar_summary.csv"), index=False)
    c.to_csv(os.path.join(RESULTS, "cultivar_comparisons.csv"), index=False)
    return dict(summary=s.to_dict("records"), comparisons=c.to_dict("records"))


if __name__ == "__main__":
    res = {"iteration1": iteration(), "robustness": robustness(), "wcp_clip": wcp_clip(), "cultivar": cultivar()}
    json.dump(res, open(os.path.join(RESULTS, "extra_results.json"), "w"), indent=1, default=float)
    print("written extra_results.json:", {k: (list(v) if isinstance(v, dict) else bool(v)) for k, v in res.items()})
