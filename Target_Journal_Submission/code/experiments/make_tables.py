"""Generate all manuscript and supplementary tables (CSV + Markdown) from result files."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.utils import RESULTS

ROOT = os.path.dirname(RESULTS)
TAB = os.environ.get("TABLE_DIR", os.path.join(ROOT, "tables"))
os.makedirs(TAB, exist_ok=True)
TASKS = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
         "corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
GEN = ["ossl_lucas_campaign", "ossl_kssl_to_lucas", "tablets"]
SHORT = {"mango_season_loso": "M-season", "mango_season_forward": "M-forward", "mango_instrument": "M-instr.",
         "mango_population": "M-pop.", "ossl_lucas_block": "S-region", "corn_moisture": "C-moist",
         "corn_oil": "C-oil", "corn_protein": "C-prot", "corn_starch": "C-starch", "ossl_lucas_campaign": "S-campaign",
         "ossl_kssl_to_lucas": "S-KSSL→LUCAS", "tablets": "Tablets"}
METHODS = ["ASTM-R", "ASTM-G", "BAG", "GPR", "QGB", "CQR", "SCP", "NCP-kNN", "CV+", "WCP", "HJ+", "HCP-D", "GC-D+", "GC-D", "ORACLE"]



def rng(v):
    """'lo–hi', or a single value when every outer fold has the same value."""
    return f"{v.min()}" if v.min() == v.max() else f"{v.min()}–{v.max()}"

def fmt(x, d=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    if isinstance(x, (float, np.floating)) and not np.isfinite(x):
        return "∞"
    return f"{x:.{d}f}"


def write(df, name, caption):
    df.to_csv(os.path.join(TAB, f"{name}.csv"), index=False)
    with open(os.path.join(TAB, f"{name}.md"), "w") as f:
        f.write(f"**{caption}**\n\n")
        f.write("| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n")
        for r in df.itertuples(index=False):
            f.write("| " + " | ".join(map(str, r)) + " |\n")


def main():
    s = pd.read_csv(os.path.join(RESULTS, "summary_results.csv"))
    # ---- Table 1: scenarios
    rows = []
    for t in TASKS + GEN:
        fs = sorted(glob.glob(os.path.join(RESULTS, "main", f"folds_{t}_seed0.csv")))
        if not fs:
            continue
        fi = pd.read_csv(fs[0])
        ng = s[(s.task == t) & (s.method == "GC-D") & (s.alpha == 0.1)]
        rows.append({"Scenario": SHORT[t], "Outer folds": len(fi),
                     "Held-out groups": int(ng.n_groups.iloc[0]) if len(ng) else "–",
                     "Training spectra": rng(fi.n_train),
                     "Test spectra (total)": int(fi.n_test.sum()),
                     "Calibration groups K": rng(fi.n_calib_groups),
                     "PLS LVs": rng(fi.A)})
    write(pd.DataFrame(rows), "table1_scenarios", "Table 1. Deployment-shift scenarios")
    # ---- Table 2/3: coverage and interval score at alpha = 0.1 (main tasks + generalisation)
    for alpha in (0.1, 0.05, 0.2):
        a = s[s.alpha == alpha]
        for metric, name, d in [("coverage", "coverage", 3), ("interval_score", "interval_score", 2), ("width", "width", 2),
                                ("coverage_min", "worst_group_coverage", 3), ("share_under", "share_groups_under", 2)]:
            tab = []
            for m in METHODS:
                r = {"Method": m}
                for t in TASKS + GEN:
                    v = a[(a.task == t) & (a.method == m)][metric]
                    r[SHORT[t]] = fmt(float(v.iloc[0]), d) if len(v) else "–"
                tab.append(r)
            write(pd.DataFrame(tab), f"table_{name}_alpha{alpha}", f"{name} at alpha = {alpha}")
    # ---- ablation table
    cells = ["R-U-A", "R-U-D", "G-U-A", "G-W-A", "G-U-D", "GC-D"]
    a = s[s.alpha == 0.1]
    tab = []
    for t in TASKS:
        r = {"Scenario": SHORT[t]}
        for c in cells:
            v = a[(a.task == t) & (a.method == c)]
            r[c] = f"{fmt(float(v.coverage.iloc[0]))} / {fmt(float(v.interval_score.iloc[0]), 2)}" if len(v) else "–"
        tab.append(r)
    write(pd.DataFrame(tab), "table_ablation", "Factorial ablation: coverage / interval score (alpha = 0.1)")
    # ---- statistics table
    c = pd.read_csv(os.path.join(RESULTS, "comparisons_alpha0.1.csv"))
    tab = []
    for t in TASKS + GEN:
        r = {"Scenario": SHORT[t]}
        r["Units"] = str(c[c.task == t].n_units.iloc[0]) if (c.task == t).any() else "–"
        for m in ["SCP", "ASTM-R", "ASTM-G", "CV+", "CQR", "WCP", "G-W-A"]:
            v = c[(c.task == t) & (c.comparator == m)]
            if len(v):
                v = v.iloc[0]
                r[m] = f"{v.IS_r_rb:+.2f} ({'<0.001' if v.IS_p_holm < 0.001 else f'{v.IS_p_holm:.3f}'})"
            else:
                r[m] = "–"
        tab.append(r)
    write(pd.DataFrame(tab), "table_statistics", "GC-D vs comparators: rank-biserial effect on interval score (Holm p)")
    # ---- timing
    tf = os.path.join(RESULTS, "timing_summary.csv")
    if os.path.exists(tf):
        tab = pd.read_csv(tf)
        for col in ["method_s", "method_s_sd", "peak_MiB", "ms_per_test_spectrum", "shared_setup_s"]:
            tab[col] = tab[col].map(lambda v: fmt(v, 3))
        write(tab, "table_timing_mango_loso", "Computing cost per held-out season (mango LOSO; isolated measurement)")
    # ---- extra tables
    for f, name, cap in [("iteration1_summary.csv", "table_iteration1", "Post-hoc iteration 1"),
                         ("iteration1_comparisons.csv", "table_iteration1_tests", "Post-hoc iteration 1: paired tests"),
                         ("robustness_groups_summary.csv", "table_robust_groups", "Robustness: number of calibration groups"),
                         ("robustness_size_summary.csv", "table_robust_size", "Robustness: training-set size"),
                         ("robustness_perturb_summary.csv", "table_robust_perturb", "Robustness: spectral perturbation"),
                         ("sensitivity_summary.csv", "table_sensitivity", "Sensitivity analysis"),
                         ("cnn_summary.csv", "table_cnn", "1D-CNN base model (mango, new season)"),
                         ("wcp_clip_summary.csv", "table_wcp_clip", "Weighted CP with and without clipped density ratios")]:
        p = os.path.join(RESULTS, f)
        if os.path.exists(p):
            d = pd.read_csv(p)
            for col in d.columns:
                if d[col].dtype.kind == "f":
                    d[col] = d[col].map(lambda v: fmt(v, 3))
            write(d, name, cap)
    for f in ["cluster_bootstrap_coverage.csv"]:
        p = os.path.join(RESULTS, "error_analysis", f)
        if os.path.exists(p):
            d = pd.read_csv(p)
            for col in ["pooled_coverage", "ci_lo", "ci_hi"]:
                d[col] = d[col].map(lambda v: fmt(v, 3))
            write(d, "table_cluster_bootstrap", "Pooled coverage with cluster-bootstrap 95% CI")
    p = os.path.join(RESULTS, "decision", "spec_limit_decisions_mango_loso.csv")
    if os.path.exists(p):
        d = pd.read_csv(p)
        d = d[d.subset == "all"].drop(columns=["subset"])
        for col in ["accepted", "false_accept_among_accepted", "false_accept_overall", "yield_of_compliant"]:
            d[col] = d[col].map(lambda v: fmt(v, 3))
        write(d, "table_decisions", "Specification-limit decisions (mango, new season)")
    print("tables written to", TAB)


if __name__ == "__main__":
    main()
