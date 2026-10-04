"""Supplementary Material (DOCX). Every table is read from code/results or code/tables."""
import json, os, subprocess, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(HERE), "code")
R = os.path.join(CODE, "results"); T = os.path.join(CODE, "tables"); F = os.path.join(CODE, "figures")


def rows_from_csv(path, cols=None, rename=None, fmt=3):
    d = pd.read_csv(path)
    if cols:
        d = d[[c for c in cols if c in d.columns]]
    for c in d.columns:
        if d[c].dtype.kind == "f":
            # |v| ≥ 1e8: the finite stand-in (statistics.tests.BIG) for an infinite interval score used in ranking
            d[c] = d[c].map(lambda v: "–" if pd.isna(v) else ("∞" if v >= 1e8 else ("−∞" if v <= -1e8 else f"{v:.{fmt}f}")))
    if rename:
        d = d.rename(columns=rename)
    return [list(map(str, d.columns))] + d.astype(str).values.tolist()


def md_table(path):
    d = pd.read_csv(path, dtype=str).fillna("–")
    return [list(d.columns)] + d.values.tolist()


def build(out):
    blocks = []
    P = lambda t: blocks.append(dict(type="p", text=t))
    H = lambda t, l=1: blocks.append(dict(type=f"h{l}", text=t))
    TAB = lambda rows, cap, note=None: blocks.append(dict(type="table", rows=rows, caption=cap, note=note))
    FIGB = lambda p, cap: blocks.append(dict(type="fig", path=p, caption=cap, width_in=6.3))
    H("S1. Method settings")
    cfg = json.load(open(os.path.join(CODE, "config", "experiment_config.json")))
    rows = [["Component", "Setting"]]
    for k, v in cfg.items():
        if k == "note":
            continue
        rows.append([k, json.dumps(v, ensure_ascii=False).replace('"', "")])
    TAB(rows, "Table S1. Fixed settings of all experiments (config/experiment_config.json).")
    H("S2. Generalisation scenarios and exchangeable control")
    s = pd.read_csv(os.path.join(R, "summary_results.csv"))
    pg = pd.read_csv(os.path.join(R, "per_group_results.csv"))
    meths = ["ASTM-R", "ASTM-G", "BAG", "GPR", "CQR", "SCP", "CV+", "WCP", "G-W-A", "GC-D", "GC-D+", "HJ+", "HCP-D", "ORACLE"]
    rows = [["Method", "S-campaign cov.", "S-campaign IS", "S-KSSL→LUCAS cov.", "S-KSSL→LUCAS IS", "Tablets inst. 1 cov.", "Tablets inst. 2 cov."]]
    a = s[s.alpha == 0.1]; b = pg[(pg.alpha == 0.1) & (pg.task == "tablets")]
    f = lambda v: "∞" if v == float("inf") else f"{v:.3f}"
    for m in meths:
        g = lambda t, c: a[(a.task == t) & (a.method == m)][c]
        tb = b[b.method == m].set_index("group").coverage
        rows.append([m, f(float(g("ossl_lucas_campaign", "coverage").iloc[0])), f(float(g("ossl_lucas_campaign", "interval_score").iloc[0])),
                     f(float(g("ossl_kssl_to_lucas", "coverage").iloc[0])), f(float(g("ossl_kssl_to_lucas", "interval_score").iloc[0])),
                     f(float(tb.get("inst1", float("nan")))), f(float(tb.get("inst2", float("nan"))))])
    TAB(rows, "Table S2. Coverage (cov.) and interval score (IS) at nominal 0.90 for the LUCAS campaign shift (2009 ↔ 2015), the "
              "KSSL → LUCAS library transfer, and the tablet data (calibration on instrument 1; test on instrument 1 = exchangeable "
              "control, instrument 2 = instrument shift without group information). Means over five seeds.")
    H("S3. Other nominal levels")
    for alpha in (0.05, 0.2):
        TAB(md_table(os.path.join(T, f"table_coverage_alpha{alpha}.csv")), f"Table S3{'a' if alpha == 0.05 else 'b'}. Group-averaged coverage at nominal {1 - alpha:.2f}.")
    H("S4. Worst-group coverage and share of under-covered groups")
    TAB(md_table(os.path.join(T, "table_worst_group_coverage_alpha0.1.csv")), "Table S4a. Lowest coverage among held-out groups (nominal 0.90).")
    TAB(md_table(os.path.join(T, "table_share_groups_under_alpha0.1.csv")), "Table S4b. Share of held-out groups with coverage below 0.85 (nominal 0.90).")
    H("S5. Sensitivity analysis")
    if os.path.exists(os.path.join(R, "sensitivity_summary.csv")):
        TAB(rows_from_csv(os.path.join(R, "sensitivity_summary.csv")), "Table S5. Sensitivity of coverage, width and interval score to the number of "
            "latent variables (A_offset), the features of the scale model (diag_mode), the floor of σ (floor_frac), the "
            "preprocessing, and the number of population folds (nominal 0.90, seed 0).")
    H("S6. Convolutional network as point predictor")
    if os.path.exists(os.path.join(R, "cnn_summary.csv")):
        TAB(rows_from_csv(os.path.join(R, "cnn_summary.csv")), "Table S6. 1D-CNN point predictor (mango, new season; group-averaged coverage over "
            "seven seasons; mean over seeds). σ(x) uses the PLS diagnostics of the same spectra.")
    H("S7. Post-hoc iteration (GC-D2, GC-CQR)")
    if os.path.exists(os.path.join(R, "iteration1_summary.csv")):
        TAB(rows_from_csv(os.path.join(R, "iteration1_summary.csv")), "Table S7a. Post-hoc variants (seeds 0–2; nominal 0.90).")
        TAB(rows_from_csv(os.path.join(R, "iteration1_comparisons.csv"),
                          ["task", "method", "comparator", "n_groups", "IS_median_diff", "IS_r_rb", "IS_p", "IS_p_holm"], fmt=4),
            "Table S7b. Paired Wilcoxon tests over held-out groups (Holm across scenarios for each contrast).")
    H("S8. Weighted conformal prediction with clipped density ratios")
    if os.path.exists(os.path.join(R, "wcp_clip_summary.csv")):
        TAB(rows_from_csv(os.path.join(R, "wcp_clip_summary.csv")), "Table S8. WCP vs WCP-clip (density ratios normalised to mean 1 on the "
            "calibration set and capped at 20); finite_frac = share of test spectra with a bounded interval.")
    H("S9. Computing cost")
    if os.path.exists(os.path.join(R, "timing_summary.csv")):
        TAB(rows_from_csv(os.path.join(R, "timing_summary.csv")), "Table S9. Isolated computing cost per held-out season (mango LOSO, ~70 000 training "
            "spectra, one CPU core, mean of three seasons).")
        FIGB(os.path.join(F, "fig7_efficiency.png"), "Fig. S2. Method-specific computing time (left, log scale) and peak additional memory (right); "
             "dashed line: shared group-wise cross-validation and final PLS fit.")
    H("S10. Pooled coverage with cluster-bootstrap confidence intervals")
    p = os.path.join(R, "error_analysis", "cluster_bootstrap_coverage.csv")
    if os.path.exists(p):
        TAB(rows_from_csv(p), "Table S10. Coverage pooled over all test spectra with 95 % cluster-bootstrap intervals (clusters = fruit or soil sample; seed 0).")
    H("S11. Specification-limit decisions")
    p = os.path.join(R, "decision", "spec_limit_decisions_mango_loso.csv")
    if os.path.exists(p):
        d = pd.read_csv(p); d = d[d.subset == "all"].drop(columns=["subset"]); d.to_csv("/tmp/claude-0/dec.csv", index=False)
        TAB(rows_from_csv("/tmp/claude-0/dec.csv"), "Table S11. Decisions 'DM ≥ L' accepted when the lower interval limit ≥ L (mango, new season, seed 0).")
    H("S12. Informativeness of the corn models on a new instrument")
    p = os.path.join(R, "error_analysis", "corn_model_informativeness.csv")
    if os.path.exists(p):
        TAB(rows_from_csv(p), "Table S12. RMSEP and bias on the held-out instrument vs. the SD of the reference values, and CQR width vs. the "
            "central 90 % range of the reference values (seed 0).")
    H("S13. Number of calibration groups")
    p = os.path.join(R, "robustness_groups_summary.csv")
    if os.path.exists(p):
        TAB(rows_from_csv(p), "Table S13. Coverage when only K training groups are used (three repetitions); finite = minimum share of bounded intervals.")
    H("S14. Paired comparisons")
    p = os.path.join(R, "comparisons_alpha0.1.csv")
    rows = rows_from_csv(p, ["task", "comparator", "unit", "n_units", "IS_median_diff", "IS_r_rb", "IS_p", "IS_p_holm", "IS_p_holm_all_main",
                             "covgap_median_diff", "covgap_p_holm"], fmt=4)
    rows[0] = ["Scenario", "Comparator", "Unit", "n", "ΔIS (median)", "r", "p", "p Holm", "p Holm (all)", "Δ|cov. gap|", "p Holm (gap)"]
    rows[1:] = [[r[0], r[1], r[2].replace("held-out group", "group").replace("outer fold (seed-0 partition)", "fold (seed 0)").replace("outer fold", "fold")] + r[3:] for r in rows[1:]]
    TAB(rows, "Table S14. All paired comparisons of GC-D with each comparator (two-sided Wilcoxon signed-rank over units; "
              "ΔIS = median of GC-D minus comparator interval score, −∞ when the comparator's intervals were unbounded; "
              "r = rank-biserial correlation; Holm within scenario and, more conservatively, across all main-scenario tests "
              "(all); Δ|cov. gap| = median difference of |coverage − 0.90|).")
    H("S15. Leave-one-cultivar-out test")
    p = os.path.join(R, "cultivar_summary.csv")
    if os.path.exists(p):
        TAB(rows_from_csv(p), "Table S15a. Leave-one-cultivar-out (mango; ten cultivars; seeds 0–2; nominal 0.90).")
        TAB(rows_from_csv(os.path.join(R, "cultivar_comparisons.csv"), fmt=4), "Table S15b. Paired comparisons of GC-D with each "
            "comparator over cultivars (two-sided Wilcoxon, Holm correction).")
    FIGB(os.path.join(F, "fig10_effect_sizes.png"), "Fig. S1. Rank-biserial effect sizes of the interval-score differences between GC-D "
         "and selected comparators (negative: GC-D lower); larger symbols: Holm-adjusted p < 0.05.")
    content = dict(meta=dict(title="Supplementary Material — Group-conformal calibration of near-infrared prediction intervals for new "
                                   "seasons, instruments and regions using PLS diagnostics",
                             authors="[Authors]", affiliations=[], corresponding="", abstract=["Supplementary tables S1–S15 and figures S1–S2. "
                             "All values are generated from the result files of the accompanying code (run_all.py)."], keywords=["Supplementary material"]),
                   blocks=blocks, references=[])
    js = out.replace(".docx", "_content.json")
    json.dump(content, open(js, "w"), indent=1, ensure_ascii=False)
    subprocess.run(["node", os.path.join(HERE, "render_docx.js"), js, out, "--single", "--no-lines"], check=True)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "supplementary", "Supplementary_Material.docx"))
