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
        TAB(md_table(os.path.join(T, f"table_coverage_alpha{alpha}.csv")), f"Table S3{'a' if alpha == 0.05 else 'b'}. Group-averaged coverage at nominal {1 - alpha:.2f}.",
            "The difference GC-D − SCP for every scenario and nominal level is listed in results/revision/alpha_consistency.csv; "
            "it has the same sign at 0.80, 0.90 and 0.95 in every mango and soil scenario.")
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
            "spectra, one CPU core, mean of three seasons).",
            "method_s and peak_MiB are measured after the shared step (group-wise cross-validation and final PLS fit, shared_setup_s), "
            "which every PLS-based method needs. Sources of the memory differences: ORACLE, ASTM-G, G-U-A and G-W-A only sort "
            "residuals that already exist (< 6 MiB); GC-D, G-U-D and GC-D+ evaluate T² and Q of every training spectrum under its "
            "out-of-group fold model, which requires reconstructing the n × p training matrix in double precision "
            "(≈ 70 000 × 103 × 8 bytes ≈ 58 MB, plus the scale-model fit); SCP, WCP and HCP fit an additional PLS model on part of the "
            "data; CV+, ASTM-R and R-U-* run a second (random) cross-validation; GPR stores the 1000 × 1000 kernel matrix and its "
            "factorisation; bagging stores 25 models.")
        FIGB(os.path.join(F, "fig7_efficiency.png"), "Fig. S1. Method-specific computing time (left, log scale) and peak additional memory (right); "
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
    FIGB(os.path.join(F, "fig10_effect_sizes.png"), "Fig. S2. Rank-biserial effect sizes of the interval-score differences between GC-D "
         "and selected comparators (negative: GC-D lower); larger symbols: Holm-adjusted p < 0.05.")
    H("S15. Leave-one-cultivar-out test")
    p = os.path.join(R, "cultivar_summary.csv")
    if os.path.exists(p):
        TAB(rows_from_csv(p), "Table S15a. Leave-one-cultivar-out (mango; ten cultivars; seeds 0–2; nominal 0.90).")
        TAB(rows_from_csv(os.path.join(R, "cultivar_comparisons.csv"), fmt=4), "Table S15b. Paired comparisons of GC-D with each "
            "comparator over cultivars (two-sided Wilcoxon, Holm correction).")
    RV = os.path.join(R, "revision")
    H("Sections S16–S28: analyses added during revision")
    P("The analyses in this part were added in response to peer review, after the main results were known (manuscript Section 3.5). "
      "They are produced by experiments/run_revision.py, experiments/run_simulation.py and experiments/revision_analyses.py.")
    SHORTV = {"logistic, C = 1, all scores + log Q (as in main runs)": "C=1, all (main)",
              "logistic, C = 0.01 (strong regularisation)": "C=0.01, all", "logistic, C = 1, first 3 scores only": "C=1, 3 scores",
              "GC-D (no correction)": "none", "GC-D, centre shifted": "shifted", "GC-D-BC (shifted and recalibrated)": "GC-D-BC",
              "default (Poisson, log(1+T²), Q/Q̃)": "default", "log-normal (LS on log|r|)": "log-normal",
              "log T² instead of log(1+T²)": "log T²", "Q not normalised by Q̃": "Q not / Q̃", "with T²×Q interaction": "T²×Q term",
              "group-weighted GLM fit": "group-weighted", "Gaussian GLM, log link": "Gaussian GLM"}
    def T_(fname, cap, cols=None, fmt=3, note=None):
        p_ = os.path.join(RV, fname)
        if os.path.exists(p_):
            d_ = pd.read_csv(p_)
            for c_ in d_.columns:
                if d_[c_].dtype == object:
                    d_[c_] = d_[c_].replace(SHORTV)
            tmp = os.path.join("/tmp/claude-0", "sup_" + fname)
            d_.to_csv(tmp, index=False)
            TAB(rows_from_csv(tmp, cols, fmt=fmt), cap, note)
    H("S16. Groups and physical units per scenario")
    T_("units_per_group.csv", "Table S16. Held-out groups, spectra, physical units, units per group (median, min, max), units that occur in more than "
       "one group, and the range of the number of calibration groups per outer fold (seed 0).")
    H("S17. Form of the scale model σ(x)")
    T_("scale_form_summary.csv", "Table S17. GC-D with alternative scale models (seed 0; group-averaged coverage, interval score and width at nominal "
       "0.90). Families: Poisson quasi-likelihood (default), Gamma, Gaussian with log link, least squares on log|r| (log-normal); features: "
       "log T² instead of log(1 + T²), Q not divided by Q̃, an added T² × Q product term; a fit weighted by the group-balanced weights; "
       "and either diagnostic alone.")
    H("S18. Strongly unequal group sizes")
    T_("unbalanced_summary.csv", "Table S18. Training groups subsampled to Zipf-like sizes (relative sizes 1, 2^−1.5, 3^−1.5, … in random order; "
       "three repetitions). largest_share: median share of the training spectra in the largest group; max_min_ratio: median ratio of the "
       "largest to the smallest group. Means over held-out groups; for the log-transformed soil OC the mean interval score and width are "
       "dominated by a few back-transformed extreme intervals, so medians over groups are also given.")
    H("S19. Interval-score differences: estimation")
    T_("effect_size_intervals.csv", "Table S19. Mean difference in interval score (GC-D − comparator) over units of analysis with 95 % percentile "
       "bootstrap interval (4000 resamples), the relative difference, the share of units in which GC-D was lower, and the posterior "
       "probability that the mean difference is negative under the Bayesian bootstrap (flat Dirichlet weights on the units). Comparators "
       "with unbounded intervals are omitted.", fmt=3)
    H("S20. Weighted conformal prediction: density-ratio estimator and cap")
    T_("wcp_variants_summary.csv", "Table S20. WCP with three density-ratio estimators (logistic classifier with C = 1 on all PLS scores and log Q, as in "
       "the main runs; with C = 0.01; with C = 1 on the first three scores only) and caps on the normalised ratios (seed 0). finite_frac: "
       "share of bounded intervals; ess_frac: effective sample size (Σw)²/Σw² of the calibration weights relative to the number of "
       "calibration spectra (median over groups); test_mass_gt_alpha: share of deployment spectra whose own weight exceeds α of the "
       "total; clf_auc: area under the ROC curve of the calibration-vs-deployment classifier.")
    H("S21. Coverage by decile of the Q ratio and of T²")
    p_ = os.path.join(RV, "conditional_coverage.csv")
    if os.path.exists(p_):
        d_ = pd.read_csv(p_)
        pv = d_.pivot_table(index=["task", "by", "decile"], columns="method", values="coverage").reset_index()
        pv["by"] = pv["by"].map({"Qr": "Q/Q̃", "T2": "T²"})
        pv.to_csv("/tmp/claude-0/cc_pivot.csv", index=False)
        TAB(rows_from_csv("/tmp/claude-0/cc_pivot.csv"), "Table S21. Coverage of SCP, ASTM-G, G-W-A and GC-D by decile of Q/Q̃ and of T² "
            "of the test spectra (deciles defined on all test spectra of the scenario; seed 0; widths in results/revision/conditional_coverage.csv).")
    H("S22. Bias correction with labelled reference samples of the new group")
    T_("bias_correction_summary.csv", "Table S22. k labelled units (fruit) of the new group: no correction (none); interval centre shifted by their mean "
       "residual (shifted); GC-D-BC (centre shifted and scale model and q̂ recalibrated on calibration residuals corrected in the same way). "
       "Evaluated on the remaining units of each group; 20 random draws; group-averaged coverage, 10th percentile and minimum of the group "
       "coverages, interval score and width (seed 0).")
    H("S23. Q-based rejection rule under test-time perturbations")
    T_("rejection_rule.csv", "Table S23. Share of new-season test spectra rejected by the rules Q/Q̃ > 95 % or 99 % quantile of the out-of-group "
       "calibration values (and, in rej_Q99_T2, also T² > its 99 % quantile), coverage of GC-D on all and on the retained spectra, "
       "coverage of SCP and RMSEP (seed 0). For the unperturbed spectra ('none') the rejected share is the false-rejection rate.")
    H("S24. Flags for uninformative intervals")
    T_("uninformative_rule.csv", "Table S24. Share of GC-D test spectra flagged because the interval is at least as wide as the central 90 % "
       "range of the training reference values, because Q/Q̃ exceeds the 99 % calibration quantile, or either; coverage and RMSEP of the "
       "flagged and retained spectra (seed 0).")
    H("S25. Specification-limit decisions over a grid of limits")
    T_("decisions_grid.csv", "Table S25a. Decisions 'y ≥ L' accepted when the lower interval limit ≥ L (mango, new season; soil, new region; seed 0). "
       "point_rule_*: acceptance when ŷ ≥ L.", cols=["task", "method", "L", "share_compliant", "false_acceptance", "yield_compliant",
                                                     "point_rule_false_acceptance", "point_rule_yield"])
    T_("decisions_break_even.csv", "Table S25b. Break-even cost ratio c* (cost of a false acceptance relative to a false rejection) above which GC-D "
       "has the lower expected cost than the comparator; empty when GC-D has both fewer false acceptances and fewer false rejections "
       "(GC-D preferable for every c) or more of both.")
    H("S26. Synthetic study of single-deployment coverage")
    P("Model: y = x'β + b_g + ε with p = 10 features, x ~ N(μ_g, I), group mean μ_g ~ N(0, I), group offset b_g ~ N(0, τ²) and "
      "heteroscedastic noise ε ~ N(0, 1 + ‖x‖²/p). A least-squares model fitted on K calibration groups (50 observations each, or "
      "log-normally distributed sizes) is deployed on a new group of 200 observations; 1000 deployments per setting. Because the group "
      "means μ_g let the model partly fit the offsets of the calibration groups, random-split residuals under-state the error for a new "
      "group, as for real spectra. GC-A: leave-one-group-out absolute residuals with group-balanced weights; GC-A+: with the "
      "finite-sample point mass.")
    p_ = os.path.join(RV, "simulation_finiteK.csv")
    if os.path.exists(p_):
        d_ = pd.read_csv(p_)
        pv = d_.pivot_table(index=["alpha", "tau", "balance", "K"], columns="method",
                            values=["mean_coverage", "sd_coverage", "share_below_nominal_minus_005"]).reset_index()
        pv.columns = [c[0] if not c[1] else f"{ {'mean_coverage': 'mean', 'sd_coverage': 'SD', 'share_below_nominal_minus_005': 'share<−0.05'}[c[0]]} {c[1]}"
                      for c in pv.columns]
        fin = d_[d_.method == "GC-A+"].set_index(["alpha", "tau", "balance", "K"]).finite_frac
        pv["GC-A+ finite"] = [fin.loc[tuple(r)] for r in pv[["alpha", "tau", "balance", "K"]].values]
        pv.to_csv("/tmp/claude-0/sim_pivot.csv", index=False)
        TAB(rows_from_csv("/tmp/claude-0/sim_pivot.csv"), "Table S26. Coverage attained in one new group (1000 deployments per setting): mean, "
            "standard deviation and share of deployments covered more than 0.05 below nominal for random-split calibration (SCP), out-of-group "
            "calibration (GC-A) and GC-A with the finite-sample point mass (GC-A+), and the share of finite GC-A+ intervals. Further statistics "
            "(10th percentile, between-group share of the variance) in results/revision/simulation_finiteK.csv.")
    FIGB(os.path.join(F, "fig11_simulation.png"), "Fig. S3. Synthetic study (τ = 1, balanced groups): (a) mean coverage minus nominal, (b) "
         "standard deviation of the coverage in one new group and (c) share of new groups covered more than 0.05 below nominal, as a "
         "function of the number of calibration groups K for α = 0.05, 0.10 and 0.20.")
    H("S27. Does a new mango population bring additional error?")
    T_("population_error_comparison.csv", "Table S27a. RMSEP of the final PLS models (GC-D centre, seed 0) for held-out populations, seasons and "
       "instruments, compared with random unit-wise 5-fold cross-validation of all mango spectra.")
    pa = os.path.join(RV, "population_absorption.json")
    if os.path.exists(pa):
        js = json.load(open(pa))
        TAB([["Quantity", "Value"]] + [[k, f"{v:.3f}" if isinstance(v, float) else str(v)] for k, v in js.items()],
            "Table S27b. Population effects: standard deviation of population-mean residuals when the population is new but its "
            "season is in training (population scenario) and when its season is new (LOSO); share of their variance explained by season "
            "(R²); share of the between-population variance of the population-mean PLS scores (A = 15, all spectra) explained by season "
            "and by season plus instrument composition.")
    H("S28. Group-to-group dispersion of coverage")
    T_("coverage_dispersion.csv", "Table S28. Standard deviation of per-group coverage, the standard deviation expected from sampling alone "
       "(binomial, with the number of physical units per group), the share of between-group variance, the 10th percentile of group "
       "coverages and the share of groups below 0.85 (seed 0).")
    content = dict(meta=dict(title="Supplementary Material — Group-conformal calibration of near-infrared prediction intervals for new "
                                   "seasons, instruments and regions using PLS diagnostics",
                             authors="[Authors]", affiliations=[], corresponding="", abstract=["Supplementary tables S1–S28 and figures S1–S3. "
                             "All values are generated from the result files of the accompanying code (run_all.py)."], keywords=["Supplementary material"]),
                   blocks=blocks, references=[])
    js = out.replace(".docx", "_content.json")
    json.dump(content, open(js, "w"), indent=1, ensure_ascii=False)
    subprocess.run(["node", os.path.join(HERE, "render_docx.js"), js, out, "--single", "--no-lines"], check=True)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "supplementary", "Supplementary_Material.docx"))
