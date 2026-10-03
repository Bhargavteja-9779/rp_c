"""E8 error analysis and E9 decision analysis from per-spectrum intervals (seed 0, alpha = 0.1).

Outputs (results/error_analysis, results/decision):
  conditional coverage by Q-ratio decile, by reference-value decile, by cultivar / temperature /
  physiological stage (mango), per-group coverage vs group bias, cluster-bootstrap CIs of coverage;
  specification-limit decisions (accept 'DM >= L' only if the interval's lower bound >= L).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.data.loaders import load_mango, load_ossl
from src.statistics.tests import cluster_bootstrap_coverage
from src.utils import RESULTS

KEY = ["GC-D", "G-W-A", "SCP", "CV+", "ASTM-R", "WCP", "CQR", "BAG", "GPR", "ORACLE"]
EA = os.path.join(RESULTS, "error_analysis"); DEC = os.path.join(RESULTS, "decision")
os.makedirs(EA, exist_ok=True); os.makedirs(DEC, exist_ok=True)


def load_points(task):
    f = os.path.join(RESULTS, "main", f"points_{task}_seed0.parquet")
    if not os.path.exists(f):
        return None
    p = pd.read_parquet(f)
    return p[(p.alpha == 0.1) & p.method.isin(KEY)].copy()


def cond_cov(p, col, bins=None, label=None):
    out = []
    for m, d in p.groupby("method"):
        x = d[col]
        if bins is not None:
            # decile edges fixed from the GC-D rows so every method uses identical bins
            cats = pd.cut(x, bins=bins, include_lowest=True, duplicates="drop")
        else:
            cats = x
        g = d.assign(cov=((d.y >= d.lo) & (d.y <= d.hi)).astype(float), w=d.hi - d.lo).groupby(cats, observed=True)
        r = g.agg(coverage=("cov", "mean"), width=("w", "mean"), n=("cov", "size")).reset_index()
        r.columns = ["bin"] + list(r.columns[1:])
        r["bin"] = r["bin"].astype(str)
        r["method"] = m; r["by"] = label or col
        out.append(r)
    return pd.concat(out, ignore_index=True)


def main():
    rows_ci = []
    for task in ["mango_season_loso", "mango_instrument", "mango_population", "ossl_lucas_block", "mango_season_forward"]:
        p = load_points(task)
        if p is None:
            print("missing points for", task); continue
        is_mango = task.startswith("mango")
        ds = load_mango() if is_mango else load_ossl("LUCAS.SSL")
        meta = ds.meta.iloc[p.idx.values].reset_index(drop=True)
        p = p.reset_index(drop=True)
        p["unit"] = meta.unit.values
        if is_mango:
            for c in ["cultivar", "temp", "physio_stage", "season"]:
                p[c] = meta[c].values
        ref = p[p.method == "GC-D"]
        qb = np.unique(np.quantile(ref.Qr, np.linspace(0, 1, 11)))
        yb = np.unique(np.quantile(ref.y, np.linspace(0, 1, 11)))
        parts = [cond_cov(p, "Qr", qb, "Q-ratio decile"), cond_cov(p, "y", yb, "reference decile")]
        if is_mango:
            parts += [cond_cov(p, c) for c in ["cultivar", "temp", "physio_stage"]]
        cc = pd.concat(parts, ignore_index=True); cc["task"] = task
        cc.to_csv(os.path.join(EA, f"conditional_coverage_{task}.csv"), index=False)
        # per-group coverage vs. group-level bias and spectral novelty
        g = p.assign(cov=((p.y >= p.lo) & (p.y <= p.hi)).astype(float), err=p.yhat - p.y).groupby(["method", "group"])
        pg = g.agg(coverage=("cov", "mean"), bias=("err", "mean"), sep=("err", "std"), medQr=("Qr", "median"),
                   width=("hi", "mean"), n=("cov", "size")).reset_index()
        pg["task"] = task
        pg.to_csv(os.path.join(EA, f"group_bias_{task}.csv"), index=False)
        # cluster-bootstrap CI of pooled coverage (clusters = fruit / soil sample)
        for m, d in p.groupby("method"):
            cov = ((d.y >= d.lo) & (d.y <= d.hi)).values
            lo, hi = cluster_bootstrap_coverage(cov, d.unit.values, n_boot=1000)
            rows_ci.append(dict(task=task, method=m, pooled_coverage=cov.mean(), ci_lo=lo, ci_hi=hi,
                                n_spectra=len(d), n_units=d.unit.nunique()))
        if task == "mango_season_loso":
            decisions(p)
    pd.DataFrame(rows_ci).to_csv(os.path.join(EA, "cluster_bootstrap_coverage.csv"), index=False)
    corn_check()


def corn_check():
    """Is the PLS model still informative on a new instrument? Compare RMSEP with the SD of the reference
    values, and CQR width with the central 90 % range of the reference values (marginal interval)."""
    from src.data.loaders import load_corn
    rows = []
    for prop in ["moisture", "oil", "protein", "starch"]:
        f = os.path.join(RESULTS, "main", f"points_corn_{prop}_seed0.parquet")
        if not os.path.exists(f):
            continue
        p = pd.read_parquet(f); p = p[p.alpha == 0.1]
        y80 = load_corn(prop).y[:80]
        marg = np.quantile(y80, 0.95) - np.quantile(y80, 0.05)
        for inst in ["m5", "mp5", "mp6"]:
            d = p[p.fold.str.startswith(inst + "_")]
            gc = d[d.method == "GC-D"]; cq = d[d.method == "CQR"]
            rows.append(dict(property=prop, test_instrument=inst, rmsep=float(np.sqrt(np.mean((gc.yhat - gc.y) ** 2))),
                             bias=float(np.mean(gc.yhat - gc.y)), sd_reference=float(np.std(y80, ddof=1)),
                             cqr_width=float(np.mean(cq.hi - cq.lo)), marginal_90_range=float(marg)))
    pd.DataFrame(rows).to_csv(os.path.join(EA, "corn_model_informativeness.csv"), index=False)


def decisions(p):
    """Accept a fruit as meeting 'DM >= L' only when the lower interval bound is >= L
    (a one-sided 95 % statement for a central 90 % interval). Report, per method and limit L:
    false-acceptance rate among accepted fruit spectra, share of all spectra wrongly accepted,
    and yield = share of truly compliant spectra accepted."""
    rows = []
    for L in [14.0, 15.0, 16.0, 17.0]:
        for m, d in p.groupby("method"):
            acc = d.lo >= L
            ok = d.y >= L
            for s, dd in [("all", d)] + [(f"season{x}", d[d.season == x]) for x in sorted(d.season.unique())]:
                a_ = dd.lo >= L; o_ = dd.y >= L
                rows.append(dict(limit=L, method=m, subset=s, n=len(dd), accepted=float(a_.mean()),
                                 false_accept_among_accepted=float((a_ & ~o_).sum() / max(1, a_.sum())),
                                 false_accept_overall=float((a_ & ~o_).mean()),
                                 yield_of_compliant=float((a_ & o_).sum() / max(1, o_.sum()))))
    pd.DataFrame(rows).to_csv(os.path.join(DEC, "spec_limit_decisions_mango_loso.csv"), index=False)


if __name__ == "__main__":
    main()
