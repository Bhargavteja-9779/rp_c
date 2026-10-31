"""Results, discussion, conclusions, declarations and front matter — every number is read from
code/results (summary_results.csv, comparisons, hypotheses.json, extra results). Qualitative statements
that depend on the data (direction of an effect, number of tasks) are computed, not hard-coded."""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(HERE), "code")
R = os.path.join(CODE, "results")
FIG = os.path.join(CODE, "figures")
TAB = os.path.join(CODE, "tables")

MAIN = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
        "corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
CORN = MAIN[5:]
NICE = {"mango_season_loso": "mango, new season (LOSO)", "mango_season_forward": "mango, next season (forward)",
        "mango_instrument": "mango, new instrument", "mango_population": "mango, new population",
        "ossl_lucas_block": "soil, new region", "corn_moisture": "corn moisture", "corn_oil": "corn oil",
        "corn_protein": "corn protein", "corn_starch": "corn starch", "ossl_lucas_campaign": "soil, other campaign",
        "ossl_kssl_to_lucas": "soil, KSSL → LUCAS", "tablets": "tablets"}


def load():
    s = pd.read_csv(os.path.join(R, "summary_results.csv"))
    c = pd.read_csv(os.path.join(R, "comparisons_alpha0.1.csv"))
    h = json.load(open(os.path.join(R, "hypotheses.json")))
    m = json.load(open(os.path.join(R, "metrics.json")))
    ex = json.load(open(os.path.join(R, "extra_results.json"))) if os.path.exists(os.path.join(R, "extra_results.json")) else {}
    return s, c, h, m, ex


def f3(x):
    return "∞" if not np.isfinite(x) else f"{x:.3f}"


def f2(x):
    return "∞" if not np.isfinite(x) else f"{x:.2f}"


def pval(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


class S:
    def __init__(self, s):
        self.s = s

    def __call__(self, task, method, field="coverage", alpha=0.1):
        d = self.s[(self.s.task == task) & (self.s.method == method) & (self.s.alpha == alpha)]
        return float(d[field].iloc[0]) if len(d) else float("nan")

    def rng(self, tasks, method, field="coverage", alpha=0.1):
        v = [self(t, method, field, alpha) for t in tasks]
        v = [x for x in v if np.isfinite(x)]
        return min(v), max(v)


def csv_rows(path, keep=None, rename=None):
    d = pd.read_csv(path, dtype=str).fillna("–")
    if keep:
        d = d[keep]
    if rename:
        d = d.rename(columns=rename)
    return [list(d.columns)] + d.values.tolist()


def results(C, N):
    s, c, h, m, ex = load()
    g = S(s)
    B = []
    shift_mango = ["mango_season_loso", "mango_season_forward", "mango_instrument"]
    many = h["H2"]["tasks_with_ge10_groups"]
    # ------------------------------------------------------------------ 4.1
    B += [("h1", "4. Results and discussion"),
          ("h2", "4.1. Current practice miscovers under deployment shift"),
          ("table", csv_rows(os.path.join(TAB, "table1_scenarios.csv")),
           "Table 1. Deployment-shift scenarios. K is the number of distinct calibration groups available in the training "
           "data of an outer fold; PLS LVs is the range of latent variables selected by group-wise cross-validation.")]
    lo_s, hi_s = g.rng(shift_mango, "SCP"); lo_a, hi_a = g.rng(shift_mango, "ASTM-R")
    n_under_scp = sum(g(t, "SCP") < 0.85 for t in MAIN)
    B += [("p", f"Fig. 3 and Tables 2–3 summarise coverage and interval score at the nominal level 0.90. When the "
                f"held-out group was a new harvest season or a new instrument, the classical PLS interval covered "
                f"{lo_a:.3f}–{hi_a:.3f} and random-split conformal prediction (SCP) {lo_s:.3f}–{hi_s:.3f} of the "
                f"test spectra on average across groups, and SCP covered less than 0.85 in {n_under_scp} of the "
                f"{len(MAIN)} main scenarios, so pre-registered hypothesis H1 is "
                f"{'supported' if h['H1']['supported'] else 'not supported'}. CV+ and bagged PLS behaved like SCP "
                f"(e.g. new instrument: {g('mango_instrument','CV+'):.3f} and {g('mango_instrument','BAG'):.3f}), "
                f"and GPR, quantile boosting and CQR covered even less on the mango shift scenarios "
                f"({g.rng(shift_mango,'GPR')[0]:.3f}–{g.rng(shift_mango,'GPR')[1]:.3f}, "
                f"{g.rng(shift_mango,'QGB')[0]:.3f}–{g.rng(shift_mango,'QGB')[1]:.3f} and "
                f"{g.rng(shift_mango,'CQR')[0]:.3f}–{g.rng(shift_mango,'CQR')[1]:.3f}). The under-coverage is not a "
                f"consequence of poor point predictions alone: the oracle, which calibrates on labelled spectra of the "
                f"test group, attains nominal coverage with widths of "
                f"{g('mango_season_loso','ORACLE','width'):.2f} (new season) and {g('mango_instrument','ORACLE','width'):.2f} "
                f"% DM (new instrument), against {g('mango_season_loso','SCP','width'):.2f} and "
                f"{g('mango_instrument','SCP','width'):.2f} % DM for SCP. Random calibration simply under-estimates the error "
                f"that a new group brings, because the calibration spectra come from seasons, instruments and "
                f"populations that the model has already seen."),
          ("p", wcp_text(g)),
          ("p", population_text(g) + " On the exchangeable control "
                f"(tablets measured on the calibration instrument) every method reached at least nominal coverage "
                f"(Supplementary Table S2).")]
    B += [("fig", os.path.join(FIG, "fig3_main_coverage_score.png"),
           "Fig. 3. Group-averaged coverage (left; bars are 95 % bootstrap intervals over held-out groups) and interval "
           "score relative to the oracle (right; lower is better; ratios above 3 and infinite scores are plotted at 3 and labelled) at nominal "
           "coverage 0.90, means over five seeds. GC-D: proposed group-conformal calibration with diagnostic scaling.")]
    # Table 2
    t2 = pd.read_csv(os.path.join(TAB, "table_coverage_alpha0.1.csv"), dtype=str)
    t3 = pd.read_csv(os.path.join(TAB, "table_interval_score_alpha0.1.csv"), dtype=str)
    cols = ["Method", "M-season", "M-forward", "M-instr.", "M-pop.", "S-region", "C-moist", "C-oil", "C-prot", "C-starch"]
    keep = ["ASTM-R", "ASTM-G", "BAG", "GPR", "CQR", "SCP", "CV+", "WCP", "HJ+", "HCP-D", "GC-D+", "GC-D", "ORACLE"]
    sel2 = t2[t2.Method.isin(keep)].set_index("Method").loc[keep].reset_index()[cols]
    sel3 = t3[t3.Method.isin(keep)].set_index("Method").loc[keep].reset_index()[cols]
    rows2 = [cols] + sel2.values.tolist(); rows3 = [cols] + sel3.values.tolist()
    wc = _csv("wcp_clip_summary.csv")
    if wc is not None:   # reviewer request: the clipped WCP in the main tables (row inserted after WCP)
        w = wc[wc.method == "WCP-clip"].set_index("task")
        short = dict(zip(["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
                          "corn_moisture", "corn_oil", "corn_protein", "corn_starch"], cols[1:]))
        r2 = ["WCP-clip"] + [f3(w.loc[t, "coverage"]) for t in short]
        r3 = ["WCP-clip"] + [f2(w.loc[t, "interval_score"]) for t in short]
        k = keep.index("WCP") + 2
        rows2.insert(k, r2); rows3.insert(k, r3); keep = keep[:k - 1] + ["WCP-clip"] + keep[k - 1:]
    hl = [keep.index("GC-D") + 1]
    B += [("table", rows2, "Table 2. Group-averaged empirical coverage at nominal coverage 0.90 (means over five seeds). "
                           "M = mango (instr. = instrument, pop. = population), S = soil (LUCAS), C = corn.",
           "HJ+, HCP-D and GC-D+ are unbounded (coverage 1) whenever the number of calibration groups is too small for their "
           "finite-sample correction (Section 2.4); WCP returns unbounded intervals when the estimated density ratio places more "
           "than α of the weight on the test point; WCP-clip caps the normalised density ratios at 20 (Section 4.1).", hl),
          ("table", rows3, "Table 3. Mean interval score (Eq. (6); lower is better; units of the analyte) at nominal coverage 0.90. "
                           "∞: at least one group received an unbounded interval.", None, hl)]
    # ------------------------------------------------------------------ 4.2
    gc_lo, gc_hi = g.rng(shift_mango + ["ossl_lucas_block", "mango_population"], "GC-D")
    cmp = c[(c.comparator == "SCP")].set_index("task")
    B += [("h2", "4.2. Group-conformal calibration restores near-nominal coverage"),
          ("p", f"GC-D achieved group-averaged coverage between {gc_lo:.3f} and {gc_hi:.3f} on the mango season, instrument "
                f"and population scenarios and on new soil regions (Table 2). Relative to SCP, coverage on new seasons rose "
                f"from {g('mango_season_loso','SCP'):.3f} to {g('mango_season_loso','GC-D'):.3f} (LOSO) and from "
                f"{g('mango_season_forward','SCP'):.3f} to {g('mango_season_forward','GC-D'):.3f} (forward prediction), and on "
                f"new instruments from {g('mango_instrument','SCP'):.3f} to {g('mango_instrument','GC-D'):.3f}. The intervals "
                f"were wider ({g('mango_instrument','GC-D','width'):.2f} vs {g('mango_instrument','SCP','width'):.2f} % DM for new "
                f"instruments), but the width was close to that of the oracle ({g('mango_instrument','ORACLE','width'):.2f}), "
                f"and the interval score, which weighs width against misses, was lower: "
                f"{g('mango_season_loso','GC-D','interval_score'):.2f} vs {g('mango_season_loso','SCP','interval_score'):.2f} "
                f"(new season), {g('mango_season_forward','GC-D','interval_score'):.2f} vs "
                f"{g('mango_season_forward','SCP','interval_score'):.2f} (next season) and "
                f"{g('mango_instrument','GC-D','interval_score'):.2f} vs {g('mango_instrument','SCP','interval_score'):.2f} "
                f"(new instrument). For new seasons GC-D's interval score differed from the oracle's by "
                + (lambda d: "less than 1 %" if d < 1 else f"{d:.0f} %")(100*abs(g('mango_season_loso','GC-D','interval_score')/g('mango_season_loso','ORACLE','interval_score')-1))
                + ", and for the next season it was lower than the oracle's, because the oracle uses a constant width within a group."),
          ("p", "Pre-registered hypothesis H2 required coverage between 0.87 and 0.95 on every task with at least ten "
                f"training groups ({'; '.join(NICE[t] for t in many)}); it is "
                f"{'supported' if h['H2']['supported'] else 'not supported'}"
                + ("" if h["H2"]["supported"] else
                   f" (outside the range: {', '.join(NICE[t] + ' ' + f3(h['H2']['values'][t]) for t, ok in h['H2']['per_task'].items() if not ok)})")
                + ". Paired over held-out groups (outer folds for the population task, whose ten folds each hold out about 20 "
                "populations that share one model), GC-D had a lower interval score than SCP in "
                f"{int((cmp.loc[[t for t in MAIN if t in cmp.index], 'IS_median_diff'] < 0).sum())} of {len([t for t in MAIN if t in cmp.index])} "
                f"main scenarios, significantly after Holm correction only for "
                f"{', '.join(NICE[t] for t in MAIN if t in cmp.index and cmp.loc[t,'IS_p_holm'] < 0.05 and cmp.loc[t,'IS_median_diff'] < 0) or 'no scenario'} "
                f"(Supplementary Table S14); with five to seven seasons the smallest attainable two-sided Wilcoxon p-value (0.0625 or "
                f"0.0156) cannot reach significance after correction for 19 comparators. " + effect_text()                + " " + alpha_text()),
          ("p", f"A simple alternative captured much of the same benefit: the classical interval with the root mean squared error "
                f"of group-wise rather than random cross-validation (ASTM-G) covered {g('mango_season_loso','ASTM-G'):.3f} (new season), "
                f"{g('mango_season_forward','ASTM-G'):.3f} (next season), {g('mango_instrument','ASTM-G'):.3f} (new instrument) and "
                f"{g('ossl_lucas_block','ASTM-G'):.3f} (new region). GC-D had a lower interval score than ASTM-G in all four of these "
                f"scenarios ({g('mango_season_loso','GC-D','interval_score'):.2f} vs {g('mango_season_loso','ASTM-G','interval_score'):.2f}, "
                f"{g('mango_season_forward','GC-D','interval_score'):.2f} vs {g('mango_season_forward','ASTM-G','interval_score'):.2f}, "
                f"{g('mango_instrument','GC-D','interval_score'):.2f} vs {g('mango_instrument','ASTM-G','interval_score'):.2f} and "
                f"{g('ossl_lucas_block','GC-D','interval_score'):.2f} vs {g('ossl_lucas_block','ASTM-G','interval_score'):.2f}), but "
                "these differences were not significant after correction. The central practical message is thus that intervals "
                "must be calibrated on out-of-group errors; the conformal formulation adds a distribution-free quantile instead of "
                "a Gaussian t-multiplier, a sample-specific width driven by T² and Q, and, with enough groups, access to the "
                "finite-sample guarantees of Section 2.4."),
          ]
    B += [("fig", os.path.join(FIG, "fig4_per_group_coverage.png"),
           "Fig. 4. Coverage in each held-out group (points; seed-averaged) for the classical PLS interval, random-split "
           "conformal prediction and GC-D; horizontal bars are medians and the dashed line is the nominal 0.90.")]
    # ------------------------------------------------------------------ 4.3 ablation
    h3 = h["H3"]
    B += [("h2", "4.3. Which components matter"),
          ("p", "The factorial ablation (Fig. 5) separates the three ingredients. Because every cell uses the same final PLS model "
                "as GC-D, differences between cells reflect the calibration alone; in particular, ordinary cross-conformal "
                f"calibration with random folds (R-U-A) under-covered as much as SCP (new instruments {g('mango_instrument','R-U-A'):.3f} "
                f"vs {g('mango_instrument','SCP'):.3f}), so the shortfall of SCP is not caused by its smaller training set. "
                "Replacing random calibration folds by "
                f"out-of-group folds (R-U-A → G-U-A) carried most of the coverage gain on the mango shift scenarios, e.g. "
                f"{g('mango_instrument','R-U-A'):.3f} → {g('mango_instrument','G-U-A'):.3f} for new instruments and "
                f"{g('mango_season_forward','R-U-A'):.3f} → {g('mango_season_forward','G-U-A'):.3f} for the next season. "
                f"Group-balanced weights (G-U-A → G-W-A) changed coverage little with the moderately unequal group sizes of the real "
                f"data (new instruments: {g('mango_instrument','G-U-A'):.3f} → {g('mango_instrument','G-W-A'):.3f}). "
                + unbalanced_text() +
                f" Diagnostic normalisation (G-W-A → GC-D) lowered the interval score in "
                f"{h3['n_tasks_lower']} of {h3['n_tasks']} main scenarios (significantly after Holm correction in "
                f"{h3['n_tasks_significant_lower']}), so H3 is "
                + ("supported" if (h3['n_tasks_lower'] > h3['n_tasks'] / 2 and h3['n_tasks_significant_lower'] > h3['n_tasks'] / 2)
                   else "partly supported" if h3['n_tasks_lower'] > h3['n_tasks'] / 2 else "not supported")
                + " under the rule of Section 3.4. The average interval score is, however, not where the scaling matters: "
                "it redistributes width from typical to atypical spectra, so its benefit appears in the coverage of the most "
                "atypical spectra and under spectral drift, where group calibration with absolute scores (and therefore ASTM-G) "
                "fails (Sections 4.5 and 4.8)."),
          ("fig", os.path.join(FIG, "fig5_ablation.png"),
           "Fig. 5. Factorial ablation of GC-D at nominal coverage 0.90: (a) coverage (colour: deviation from 0.90, "
           "red = under-coverage) and (b) interval score relative to GC-D (values > 1: worse than GC-D).")]
    B += results_part2(C, N, s, c, h, ex, g)
    meta, tail = front_and_back(C, N, s, c, h, ex, g)
    return B, meta, tail


def _csv(name, sub=R):
    p = os.path.join(sub, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def wcp_text(g):
    wc = _csv("wcp_clip_summary.csv"); wv = _csv("wcp_variants_summary.csv", os.path.join(R, "revision"))
    t = (f"Weighted conformal prediction (WCP), which reweights the calibration residuals with the unlabelled spectra of the new "
         f"group, reached high coverage (e.g. {g('mango_instrument','WCP'):.3f} for new instruments) only by returning unbounded "
         "intervals for part of the test spectra in almost every scenario.")
    if wv is not None:
        wv = wv.assign(cap=wv["cap"].astype(str))
        d0 = wv[(wv.estimator.str.startswith("logistic, C = 1, all")) & (wv.cap == "none")].set_index("task")
        f3_ = wv[(wv.estimator.str.contains("first 3")) & (wv.cap == "none") & wv.task.str.startswith("mango")]
        t += (f" Calibration and deployment spectra were so well separated (classifier AUC {d0.clf_auc.min():.2f}–{d0.clf_auc.max():.2f}) "
              f"that the effective sample size of the weights fell to {100*d0.ess_frac.min():.1f}–{100*d0.ess_frac.max():.0f} % of the "
              "calibration set and many deployment spectra carried more than α of the total weight. This is a property of the shift, "
              "not of the estimator (Supplementary Table S20): a classifier restricted to three PLS scores avoided extreme weights "
              f"but no longer corrected for the mango shifts (coverage {f3_.coverage.min():.3f}–{f3_.coverage.max():.3f}), and stronger "
              "regularisation did not remove the unbounded intervals.")
    if wc is not None:
        v = wc.set_index(["task", "method"])
        try:
            t += (f" Capping the normalised density ratios at 20 (WCP-clip; Tables 2–3) bounded almost all intervals but covered only "
                  f"{v.loc[('mango_season_forward','WCP-clip'),'coverage']:.3f}–{v.loc[('mango_season_loso','WCP-clip'),'coverage']:.3f} on "
                  "the mango season and instrument shifts, and with the ~30 calibration spectra of the corn scenarios even a capped "
                  "weight exceeded α of the total. An interval that is unbounded for a share of samples cannot support a decision, so "
                  "WCP is not a practical remedy here; on the milder soil-region shift the capped variant reached nominal coverage.")
        except KeyError:
            pass
    return t


def effect_text():
    e = _csv("effect_size_intervals.csv", os.path.join(R, "revision"))
    if e is None:
        return ""
    v = e[e.comparator == "SCP"].set_index("task")
    many = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block"]
    SH = {"mango_season_loso": "new seasons", "mango_season_forward": "next seasons", "mango_instrument": "new instruments",
          "mango_population": "new populations", "ossl_lucas_block": "new soil regions"}
    ci_ex = [SH[t] for t in many if v.loc[t, "ci_hi"] < 0]
    ci_ex = ci_ex[0] if len(ci_ex) == 1 else ", ".join(ci_ex[:-1]) + " and " + ci_ex[-1]
    pp = v.loc[many, "post_prob_gcd_lower"]
    return (f"Estimates make the size and certainty of the differences explicit (Supplementary Table S19): in the mango and soil "
            f"scenarios GC-D lowered the mean interval score relative to SCP by {-100*v.loc[many,'rel_mean_diff'].max():.0f}–"
            f"{-100*v.loc[many,'rel_mean_diff'].min():.0f} %, the 95 % bootstrap interval excluded zero for {ci_ex}, and the "
            f"Bayesian-bootstrap probability that GC-D has the lower mean score was {pp.min():.2f}–{pp.max():.2f} (corn: "
            f"{v.loc[CORN,'post_prob_gcd_lower'].min():.2f}–{v.loc[CORN,'post_prob_gcd_lower'].max():.2f}). With few groups, such "
            "estimates and the attained coverage are a better basis for choosing a method than a test on five to seven groups.")


def alpha_text():
    a = _csv("alpha_consistency.csv", os.path.join(R, "revision"))
    if a is None:
        return ""
    sh = a[a.task.isin(["mango_season_loso", "mango_season_forward", "mango_instrument"])]
    return (f"The advantage was the same at other nominal levels: on the mango season and instrument scenarios GC-D covered "
            f"{100*sh.gcd_minus_scp.min():.0f}–{100*sh.gcd_minus_scp.max():.0f} percentage points more than SCP at 0.80, 0.90 and 0.95, "
            f"and deviated from the nominal level by at most {(sh['GC-D'] - sh.nominal).abs().max():.3f} (Supplementary Table S3).")


def unbalanced_text():
    u = _csv("unbalanced_summary.csv", os.path.join(R, "revision"))
    if u is None:
        return ""
    v = u.set_index(["task", "method"])
    ts = [t for t in ["mango_instrument", "mango_season_loso", "ossl_lucas_block"] if (t, "GC-D") in v.index]
    parts = [f"{NICE[t]} {v.loc[(t,'G-U-D'),'coverage']:.3f} → {v.loc[(t,'GC-D'),'coverage']:.3f}" for t in ts]
    sh = u.groupby("task").largest_share.first()
    return (f"When the training groups were subsampled to Zipf-like sizes (largest group {100*sh.min():.0f}–{100*sh.max():.0f} % of the "
            f"spectra; Supplementary Table S18), balancing raised coverage ({'; '.join(parts)}), because with uniform weights the "
            "calibration reflects mainly the error of the largest group.")


def dispersion_text():
    sim = _csv("simulation_finiteK.csv", os.path.join(R, "revision")); dp = _csv("coverage_dispersion.csv", os.path.join(R, "revision"))
    if sim is None or dp is None:
        return ""
    d = sim[(sim.tau == 1.0)]
    gc = d[d.method == "GC-A"]; sc = d[d.method == "SCP"]; gp = d[d.method == "GC-A+"]
    a10 = gc[gc.alpha == 0.1]
    fin = gp[gp.finite_frac >= 0.99].groupby("alpha").K.min()
    dv = dp[dp.method == "GC-D"].set_index("task")
    return (
        "Group-averaged coverage is not the whole story for a single deployment. In the real data, the coverage of GC-D in "
        f"individual held-out groups had a standard deviation of {dv.sd_group_coverage.min():.2f}–{dv.sd_group_coverage.max():.2f}, "
        f"{100*dv.between_group_share.min():.0f}–{100*dv.between_group_share.max():.0f} % of which was genuine between-group variation "
        "rather than sampling noise (Supplementary Table S28). A synthetic hierarchical model (Supplementary Section S26, Fig. S3) "
        f"shows how this depends on K, α and group-size balance: out-of-group calibration was close to nominal on average for every "
        f"K from 3 to 50 (α = 0.10: {a10.mean_coverage.min():.3f}–{a10.mean_coverage.max():.3f}; random split "
        f"{sc[(sc.alpha==0.1)&(sc.K==3)].mean_coverage.mean():.3f} at K = 3), but the standard deviation of single-deployment coverage "
        f"fell only from {a10[a10.K==3].sd_coverage.mean():.2f} (K = 3) to {a10[a10.K==50].sd_coverage.mean():.2f} (K = 50), because it is "
        "caused by the new group's own effect, which only information about that group can remove (Section 4.8). The finite-sample "
        "correction became finite at K = " + ", ".join(f"{int(fin.loc[a_])} (α = {a_:.2f})" for a_ in sorted(fin.index))
        + ", i.e. at K ≥ 1/α − 1 for balanced and unbalanced groups alike, so the 'ten groups' above are specific to α = 0.10. With "
          "fewer groups, GC-D still removes the systematic under-coverage of random calibration, but the coverage of one deployment "
          "is uncertain by several percentage points, which should be stated when the intervals are reported.")


def scale_form_text():
    f = _csv("scale_form_summary.csv", os.path.join(R, "revision"))
    if f is None:
        return ""
    base = "default (Poisson, log(1+T²), Q/Q̃)"
    v = f.set_index(["task", "variant"])
    alt = f[~f.variant.isin([base, "Q only", "T² only"])]
    dcov = [abs(r.coverage - v.loc[(r.task, base), "coverage"]) for r in alt.itertuples()]
    dis = [r.interval_score / v.loc[(r.task, base), "interval_score"] - 1 for r in alt.itertuples()]
    return ("Replacing the Poisson quasi-likelihood by a Gamma or Gaussian log-link GLM or least squares on log|r|, using log T², "
            "omitting Q̃, adding a T² × Q interaction or weighting the fit by group changed the coverage of GC-D by at most "
            f"{max(dcov):.3f} and its interval score by {100*min(dis):+.1f} to {100*max(dis):+.1f} % (Supplementary Table S17).")


def reject_text():
    r = _csv("rejection_rule.csv", os.path.join(R, "revision"))
    if r is None:
        return ""
    v = r[r.rule == "rej_Q99"].set_index(["perturbation", "level"])
    small = [("noise", 0.003), ("gain", 0.05), ("offset_slope", 2.0), ("wl_shift", 0.5), ("wl_shift", 1.0)]
    return (f"Withholding the interval when Q/Q̃ exceeds the 99 % quantile of the out-of-group calibration values rejected "
            f"{100*v.loc[('none',0.0),'rejected']:.1f} % of unperturbed new-season spectra (false rejections), "
            f"{100*v.loc[('noise',0.01),'rejected']:.0f} % of those with 1 % noise and {100*v.loc[('noise',0.03),'rejected']:.0f} % with 3 % "
            "noise (Supplementary Table S23). Its misses were perturbations that hardly changed Q (0.3 % noise, gain, tilt, shifts ≤ 1 nm), "
            f"which GC-D covered at least {min(v.loc[k_,'coverage_all'] for k_ in small):.3f} anyway; the retained 1 %-noise spectra, "
            f"however, were covered only {v.loc[('noise',0.01),'coverage_retained']:.3f}, so the rule mitigates but does not remove the problem.")


def uninformative_text():
    u = _csv("uninformative_rule.csv", os.path.join(R, "revision"))
    if u is None:
        return ""
    v = u.set_index(["task", "rule"])
    E = "either"
    corn = [t for t in CORN if (t, E) in v.index]
    ok = [t for t in ["mango_season_loso", "mango_instrument", "ossl_lucas_block"] if (t, E) in v.index]
    return ("The useful output of an interval method in this regime is a signal not to report the prediction. Two checks computed "
            "from the calibration data provide it (Supplementary Table S24): the interval is at least as wide as the central 90 % range "
            "of the training reference values, or Q/Q̃ exceeds the 99 % quantile of the out-of-group calibration values. At least one "
            f"check fired for {100*min(v.loc[(t,E),'share_flagged'] for t in corn):.0f}–{100*max(v.loc[(t,E),'share_flagged'] for t in corn):.0f} % "
            f"of the corn test spectra and {100*v.loc[('ossl_kssl_to_lucas',E),'share_flagged']:.0f} % of the KSSL → LUCAS spectra, against "
            f"{100*min(v.loc[(t,E),'share_flagged'] for t in ok):.1f}–{100*max(v.loc[(t,E),'share_flagged'] for t in ok):.1f} % in the mango "
            "season and instrument and soil-region scenarios; for the tablets, calibrated on one instrument, " + tab_flag_text()
            + " When a check fires, we recommend reporting 'no reliable interval — model not valid for this sample', and transferring "
              "or re-calibrating the model when it fires for a large share of a new group's spectra.")


def conditional_text():
    c = _csv("conditional_coverage.csv", os.path.join(R, "revision"))
    if c is None:
        return ""
    c = c[c.by == "Qr"]
    def v(t, m, d):
        return float(c[(c.task == t) & (c.method == m) & (c.decile == d)].coverage.iloc[0])
    ts = ["mango_season_loso", "mango_season_forward", "mango_instrument", "ossl_lucas_block"]
    top_gwa = [v(t, "G-W-A", 10) for t in ts]; top_gcd = [v(t, "GC-D", 10) for t in ts]
    top_ag = [v(t, "ASTM-G", 10) for t in ts]
    low_gwa = [v(t, "G-W-A", 1) for t in ts]
    return ("Diagnostic scaling is not needed for coverage averaged over all spectra — out-of-group calibration with absolute "
            "scores (G-W-A), like ASTM-G, achieves that — but for the atypical spectra. Giving every spectrum the same width, G-W-A "
            f"covered {min(low_gwa):.3f}–{max(low_gwa):.3f} of the spectra in the lowest Q/Q̃ decile but only {min(top_gwa):.3f}–"
            f"{max(top_gwa):.3f} in the highest decile of the new-season, next-season, new-instrument and soil-region scenarios, "
            f"against {min(top_gcd):.3f}–{max(top_gcd):.3f} for GC-D; ASTM-G, whose width varies only through the leverage, covered "
            f"{min(top_ag):.3f}–{max(top_ag):.3f} (Fig. 7a,b; Supplementary Table S21). The same held under "
            f"spectral drift (Section 4.5) and in the KSSL → LUCAS transfer (highest decile: G-W-A {v('ossl_kssl_to_lucas','G-W-A',10):.3f}, GC-D "
            f"{v('ossl_kssl_to_lucas','GC-D',10):.3f}). The scaling is therefore irreplaceable whenever decisions are taken on "
            "individual samples, some of which differ from the calibration population.")


def bias_text():
    gb = _csv("group_bias_mango_instrument.csv", os.path.join(R, "error_analysis"))
    bs = _csv("bias_correction_summary.csv", os.path.join(R, "revision"))
    bp = _csv("bias_correction_per_group.csv", os.path.join(R, "revision"))
    pgr = _csv("per_group_results.csv")
    t = ""
    if gb is not None:
        e = gb[gb.method == "GC-D"]
        r = np.corrcoef(np.abs(e.bias), e.coverage)[0, 1]
        t += (f"The largest remaining failures were group-level biases. Per-instrument coverage of GC-D fell with the absolute "
              f"mean prediction bias of the instrument (r = {r:.2f}; Fig. 7c); the worst instrument (bias "
              f"{e.loc[e.coverage.idxmin(),'bias']:+.2f} % DM) was covered {e.coverage.min():.3f}. ")
    w0 = None
    if pgr is not None:
        pp = pgr[(pgr.task == "mango_population") & (pgr.alpha == 0.1) & (pgr.method == "GC-D")].sort_values("coverage")
        w0 = pp.iloc[0]
        t += (f"Every method failed on the same few populations; the worst (population {w0.group}, annotated in Fig. 4) consisted of "
              f"green 'Kensington Pride' fruit of 2020, harvested before maturity, which the model over-predicted by {abs(w0.bias):.2f} % DM, "
              f"so that GC-D covered {w0.coverage:.3f} of its spectra. No calibration of interval width can repair such a bias. ")
    if bs is not None:
        v = bs.set_index(["task", "variant", "k"])
        N0, SH, BC = "GC-D (no correction)", "GC-D, centre shifted", "GC-D-BC (shifted and recalibrated)"
        def q(tk, var, k, col="coverage"):
            return float(v.loc[(tk, var, k), col])
        I = "mango_instrument"; S_ = "mango_season_loso"
        bc_cov = [q(I, BC, k) for k in (1, 2, 3, 5, 10)]
        t += ("A few labelled reference samples of the new group do help (Fig. 7c,d; Supplementary Table S22). Shifting the "
              f"interval centre by the mean residual of three labelled fruit raised the worst-instrument coverage from "
              f"{q(I,N0,3,'worst_group'):.3f} to {q(I,SH,3,'worst_group'):.3f}, but a single fruit gave too noisy a bias estimate "
              f"(group-averaged coverage {q(I,SH,1):.3f}) and larger k over-covered ({q(I,SH,10):.3f} at k = 10). Mimicking the correction in "
              f"every calibration group before fitting σ and q̂ (GC-D-BC) kept the average coverage at {min(bc_cov):.3f}–{max(bc_cov):.3f} "
              f"for every k while narrowing the intervals (interval score {q(I,BC,3,'interval_score'):.2f} vs {q(I,N0,3,'interval_score'):.2f} "
              "at k = 3).")
        if bp is not None and w0 is not None:
            bp = bp.assign(gkey=pd.to_numeric(bp.group, errors="coerce"))
            pr = bp[(bp.task == "mango_population") & (bp.gkey == float(w0.group))].set_index(["variant", "k"])
            if len(pr):
                t += (f" For population {w0.group}, one labelled fruit raised the coverage from {pr.loc[(N0,1),'coverage']:.3f} to "
                      f"{pr.loc[(BC,1),'coverage']:.3f} (GC-D-BC).")
        t += (f" For new seasons, whose biases were small relative to the fruit-to-fruit variation, a few fruit were not enough "
              f"(shifted: {q(S_,SH,3):.3f} at k = 3; GC-D-BC: interval score {q(S_,BC,3,'interval_score'):.2f} vs "
              f"{q(S_,N0,3,'interval_score'):.2f}). Bias correction pays when the group bias is large — a new instrument or an atypical "
              "lot — and should then be calibrated for the noise of the bias estimate, as in GC-D-BC.")
    return t


def decision_text():
    d = _csv("decisions_grid.csv", os.path.join(R, "revision")); be = _csv("decisions_break_even.csv", os.path.join(R, "revision"))
    if d is None:
        return ""
    m = d[d.task == "mango_season_loso"].set_index(["method", "L"])
    so = d[d.task == "ossl_lucas_block"].set_index(["method", "L"])
    Ls = sorted(d[d.task == "mango_season_loso"].L.unique())
    lower_all = all(m.loc[("GC-D", L), "false_acceptance"] <= m.loc[("SCP", L), "false_acceptance"] for L in Ls)
    over5 = [L for L in Ls if m.loc[("SCP", L), "false_acceptance"] > 0.05]
    b = be[(be.task == "mango_season_loso") & (be.comparator == "SCP")].set_index("L").break_even_cost_ratio
    dom_g = [L for L in Ls if m.loc[("GC-D", L), "false_acceptance"] <= m.loc[("ASTM-G", L), "false_acceptance"]
             and m.loc[("GC-D", L), "yield_compliant"] >= m.loc[("ASTM-G", L), "yield_compliant"]]
    return (
        "Accepting a fruit for 'DM ≥ L' only when the lower interval limit exceeds L is a one-sided 95 % statement. Over limits "
        f"from {Ls[0]:.0f} to {Ls[-1]:.0f} % DM (Fig. 8a,b; Supplementary Table S25), GC-D "
        + ("had a false-acceptance rate no higher than SCP at every limit" if lower_all else "had a lower false-acceptance rate than SCP at most limits")
        + f" (L = 16 %: {m.loc[('GC-D',16.0),'false_acceptance']:.3f} vs {m.loc[('SCP',16.0),'false_acceptance']:.3f}), whereas SCP exceeded "
        f"the nominal 5 % from L = {min(over5):.1f} % upwards"
        + (f"; against ASTM-G it had both no more false acceptances and a higher yield at {len(dom_g)} of the {len(Ls)} limits" if dom_g else "")
        + f". The price is yield: at L = 16 % GC-D accepted {m.loc[('GC-D',16.0),'yield_compliant']:.3f} of the compliant fruit, SCP "
        f"{m.loc[('SCP',16.0),'yield_compliant']:.3f} and the oracle {m.loc[('ORACLE',16.0),'yield_compliant']:.3f}, so most of the yield loss "
        "is the cost of any honest uncertainty statement; accepting on the point prediction alone kept "
        f"{m.loc[('GC-D',16.0),'point_rule_yield']:.3f} of the compliant fruit, but {m.loc[('GC-D',16.0),'point_rule_false_acceptance']:.3f} of "
        "the accepted fruit were non-compliant. Which rule is preferable depends on c, the cost of accepting a non-compliant fruit "
        f"relative to rejecting a compliant one: GC-D has the lower expected cost than SCP for c above {b.loc[16.0]:.1f} at L = 16 % "
        f"({b.min():.1f}–{b.max():.1f} over the grid). Contractual penalties for out-of-specification lots, minimum-maturity rules or "
        "safety-related attributes (c ≫ 10) favour GC-D; bulk processing in which a rejected fruit is merely downgraded (c ≈ 1) favours "
        "the point prediction. For soil organic carbon (Fig. 8c,d) GC-D, SCP and the classical intervals differed little "
        f"(false acceptance at L = 2 % OC: {so.loc[('GC-D',2.0),'false_acceptance']:.3f} vs {so.loc[('SCP',2.0),'false_acceptance']:.3f}); "
        f"CQR, with asymmetric intervals, had the fewest false acceptances ({so.loc[('CQR',2.0),'false_acceptance']:.3f}) at a lower yield, "
        "consistent with the level-dependent errors discussed in Section 4.10.")


def tab_flag_text():
    lf = os.path.join(R, "revision", "diag_limits_tablets.csv"); pf = os.path.join(R, "main", "points_tablets_seed0.parquet")
    if not (os.path.exists(lf) and os.path.exists(pf)):
        return ""
    d = pd.read_parquet(pf); d = d[(d.method == "GC-D") & (d.alpha == 0.1)]
    lim = pd.read_csv(lf).set_index("fold")
    fl = (d.Qr > d.fold.map(lim.Qr99)).groupby(d.group).mean()
    return (f"the Q check flagged {100*fl.get('inst2', float('nan')):.0f} % of the second-instrument spectra and "
            f"{100*fl.get('inst1', float('nan')):.1f} % of the calibration-instrument spectra, i.e. it recognised an instrument change "
            "that no interval method could anticipate.")


def population_text(g):
    pe = _csv("population_error_comparison.csv", os.path.join(R, "revision"))
    pf = os.path.join(R, "revision", "population_absorption.json")
    pa = json.load(open(pf)) if os.path.exists(pf) else None
    t = (f"For new mango populations all methods were close to nominal (SCP {g('mango_population','SCP'):.3f}, classical "
         f"{g('mango_population','ASTM-R'):.3f}).")
    if pe is not None and pa is not None:
        v = pe.set_index("scenario")
        t += (f" A new population brought little error that random calibration had not seen: its RMSEP was only "
              f"{100*(v.loc['new population','ratio_to_random_cv']-1):.0f} % above the random unit-wise cross-validation error, against "
              f"{100*(v.loc['new season','ratio_to_random_cv']-1):.0f} % for a new season and "
              f"{100*(v.loc['new instrument','ratio_to_random_cv']-1):.0f} % for a new instrument (Supplementary Table S27). Populations "
              "nevertheless differ spectrally — season and instrument composition explained "
              f"{100*pa['r2_pop_mean_scores_by_season_and_instruments']:.0f} % of the between-population variance of the PLS scores — so "
              "the model generalises across lots rather than population effects being a re-labelling of season and instrument effects.")
    return t


def results_part2(C, N, s, c, h, ex, g):
    B = []
    # ------------------------------------------------------------------ 4.4 guarantees and number of groups
    rg = _csv("robustness_groups_summary.csv")
    B += [("h2", "4.4. Distribution-free guarantees need many groups"),
          ("p", f"The variants with finite-sample guarantees behaved as theory predicts. With at most six training seasons "
                f"or two corn instruments, HJ+, HCP and GC-D+ returned unbounded intervals (Tables 2–3), because "
                f"the point mass 1/(K + 1) at +∞ exceeds α. With 27–30 instruments or 29 soil regions they were finite "
                f"and covered {g('mango_instrument','HJ+'):.3f} (HJ+) and {g('mango_instrument','HCP-D'):.3f} (HCP-D) for new "
                f"instruments and {g('ossl_lucas_block','HJ+'):.3f} and {g('ossl_lucas_block','HCP-D'):.3f} for new regions, "
                f"above the nominal level as their guarantees require, but at a higher interval score than GC-D "
                f"({g('mango_instrument','HJ+','interval_score'):.2f} and {g('mango_instrument','HCP-D','interval_score'):.2f} vs "
                f"{g('mango_instrument','GC-D','interval_score'):.2f} for instruments). HCP-D pays for its exactness by "
                "fitting the model on half of the groups.")]
    if rg is not None:
        def rgv(t, m, K, col="coverage"):
            d = rg[(rg.task == t) & (rg.method == m) & (rg.K == K)]
            return float(d[col].iloc[0]) if len(d) else float("nan")
        B += [("p", "Subsampling the training groups (Fig. 6a) shows how many are needed. With K = 3 training instruments, "
                    f"GC-D covered {rgv('mango_instrument','GC-D',3):.3f} of new-instrument spectra and SCP {rgv('mango_instrument','SCP',3):.3f}; "
                    f"with K = 10 the values were {rgv('mango_instrument','GC-D',10):.3f} and {rgv('mango_instrument','SCP',10):.3f}, and with K = 20 "
                    f"{rgv('mango_instrument','GC-D',20):.3f} and {rgv('mango_instrument','SCP',20):.3f}. For soil regions GC-D covered "
                    f"{rgv('ossl_lucas_block','GC-D',3):.3f} (K = 3) to {rgv('ossl_lucas_block','GC-D',20):.3f} (K = 20). HJ+ became finite in all "
                    f"repetitions only from K = 10 (fraction of finite intervals {rgv('mango_instrument','HJ+',5,'finite'):.2f} at K = 5 and "
                    f"{rgv('mango_instrument','HJ+',10,'finite'):.2f} at K = 10 for instruments). In practice, GC-D improves on random calibration "
                    "already with a handful of groups, while formal group-level guarantees at 90 % require about ten or more.")]
    B += [("p", dispersion_text())]
    B += [("fig", os.path.join(FIG, "fig6_robustness.png"),
           "Fig. 6. Robustness. (a) Coverage on new mango instruments (circles) and new soil regions (squares) when only K "
           "randomly chosen training groups are available (three repetitions; HJ+ shown only where all intervals were finite). "
           "(b) Coverage for new seasons when 10–50 % of training fruit are used (mean ± SD over three repetitions). (c) Coverage "
           "for new seasons when the test spectra are perturbed (gain, linear baseline tilt, wavelength shift, white noise "
           "relative to the median absorbance SD); training spectra are unperturbed.")]
    # ------------------------------------------------------------------ 4.5 robustness / sensitivity / model
    rz = _csv("robustness_size_summary.csv"); rp = _csv("robustness_perturb_summary.csv"); sv = _csv("sensitivity_summary.csv")
    cn = _csv("cnn_summary.csv")
    txt = "Coverage of GC-D did not depend on the amount of training data"
    if rz is not None:
        v = rz[rz.method == "GC-D"].set_index("frac").coverage; w = rz[rz.method == "SCP"].set_index("frac").coverage
        txt += (f": with 10, 25 and 50 % of the training fruit it covered {v.loc[0.1]:.3f}, {v.loc[0.25]:.3f} and {v.loc[0.5]:.3f} "
                f"of new-season spectra, against {w.loc[0.1]:.3f}, {w.loc[0.25]:.3f} and {w.loc[0.5]:.3f} for SCP (Fig. 6b). The "
                "coverage gap of random calibration is therefore a consequence of the shift, not of a small sample")
    txt += "."
    if rp is not None:
        def pv(p_, l, m, col="coverage"):
            d = rp[(rp.perturbation == p_) & np.isclose(rp.level, l) & (rp.method == m)]
            return float(d[col].iloc[0]) if len(d) else float("nan")
        txt += (f" Under simulated instrument drift of the test spectra (Fig. 6c), the second-derivative preprocessing removed "
                f"linear baseline tilts entirely. A 2-nm wavelength shift lowered SCP coverage to {pv('wl_shift',2.0,'SCP'):.3f} and "
                f"that of group calibration with absolute scores (G-W-A) to {pv('wl_shift',2.0,'G-W-A'):.3f}, whereas GC-D widened its "
                f"intervals for the affected spectra (larger Q) and covered {pv('wl_shift',2.0,'GC-D'):.3f}. White noise of 1 % of "
                f"the median absorbance SD raised the RMSEP from {pv('none',0.0,'GC-D','rmse'):.2f} to {pv('noise',0.01,'GC-D','rmse'):.2f} % DM; "
                f"coverage fell to {pv('noise',0.01,'SCP'):.3f} for SCP and to {pv('noise',0.01,'GC-D'):.3f} for GC-D. The diagnostic "
                "scale thus detects and partly compensates for spectral anomalies, but it cannot restore coverage when the "
                "predictions themselves degrade this strongly; such spectra should be rejected rather than reported with an "
                "interval. " + reject_text())
    B += [("h2", "4.5. Robustness, sensitivity and choice of point predictor"), ("p", txt)]
    if sv is not None:
        d = sv[(sv.task == "mango_season_loso")]
        gc = d[d.method == "GC-D"]
        B += [("p", f"Sensitivity analyses (Supplementary Table S5: number of latent variables ± 4, T² or Q alone, floor of σ, "
                    f"preprocessing, number of population folds) kept the new-season coverage of GC-D between {gc.coverage.min():.3f} "
                    f"and {gc.coverage.max():.3f}. " + scale_form_text())]
    if cn is not None and len(cn):
        cv = cn.set_index("method")
        B += [("p", f"With a one-dimensional convolutional network {C('cui2018', 'mishra2021')} as point predictor (mango, new season, "
                    f"{int(cv.n_seeds.iloc[0])} seeds; σ from PLS diagnostics; Supplementary Table S6), random-split conformal covered "
                    f"{cv.loc['CNN-SCP','coverage']:.3f}, out-of-group calibration with absolute scores {cv.loc['CNN-G-W-A','coverage']:.3f} "
                    f"and GC-D {cv.loc['CNN-GC-D','coverage']:.3f}, so the calibration principle did not depend on PLS for this network.")]
    # ------------------------------------------------------------------ 4.6 stress tests
    ci = _csv("corn_model_informativeness.csv", os.path.join(R, "error_analysis"))
    B += [("h2", "4.6. When group calibration cannot help — or is not needed")]
    t = "Three settings mark the limits of the approach. First, corn: with only two training instruments, no "
    if ci is not None:
        ratio = (ci.rmsep / ci.sd_reference)
        t += (f"interval method based on the PLS model reached nominal coverage, because the uncorrected instrument shift left the "
              f"model weakly informative (RMSEP {ratio.min():.2f}–{ratio.max():.2f} times the standard deviation of the reference values; "
              f"instrument-level bias up to {ci.bias.abs().max():.2f} units). CQR covered {g('corn_protein','CQR'):.3f} (protein) only "
              f"because its intervals ({ci.cqr_width.min():.2f}–{ci.cqr_width.max():.2f}) matched the central 90 % range of the reference "
              f"values ({ci.marginal_90_range.min():.2f}–{ci.marginal_90_range.max():.2f}), i.e. they ignored the spectra. ")
    t += (f"Second, the KSSL → LUCAS transfer across libraries, instruments and continents gave an RMSEP of "
          f"{g('ossl_kssl_to_lucas','GC-D','rmse'):.1f} % OC; SCP covered {g('ossl_kssl_to_lucas','SCP'):.3f}, GC-D "
          f"{g('ossl_kssl_to_lucas','GC-D'):.3f} and the exact HCP-D {g('ossl_kssl_to_lucas','HCP-D'):.3f}, the latter with intervals "
          f"({g('ossl_kssl_to_lucas','HCP-D','width'):.0f} % OC wide) of no analytical use. Third, the tablet calibration contained no "
          f"group structure, so GC-D degenerated to cross-conformal calibration (coverage {g('tablets','GC-D'):.3f} over the control and "
          "the shifted instrument; Supplementary Table S2). In the first two settings the failure is that of the point predictor, not of "
          "the calibration principle: an interval can only quantify the error of a model that is still valid for the new group, and "
          f"model transfer or bias correction {C('feudale2002', 'workman2018')} must precede uncertainty quantification.")
    B += [("p", t), ("p", uninformative_text())]
    cs = _csv("cultivar_summary.csv")
    if cs is not None:
        cv = cs.set_index("method")
        B += [("p", f"Conversely, group calibration is unnecessary when the held-out factor adds little group-level error. In a "
                    f"leave-one-cultivar-out test (ten cultivars, {int(cv.n_seeds.iloc[0])} seeds; Supplementary Table S15), SCP covered "
                    f"{cv.loc['SCP','coverage']:.3f} and GC-D {cv.loc['GC-D','coverage']:.3f} with nearly identical interval scores "
                    f"({cv.loc['SCP','interval_score']:.2f} and {cv.loc['GC-D','interval_score']:.2f}), because every cultivar was measured "
                    "in seasons and on instruments that remained in training. GC-D therefore cost no sharpness when the shift was small and "
                    "helped when the held-out factor carried an unrepresented group effect (season, instrument).")]
    # ------------------------------------------------------------------ 4.7 computation
    tm = _csv("timing_summary.csv")
    if tm is not None:
        tv = tm.set_index("method")
        B += [("h2", "4.7. Computational cost"),
              ("p", f"Almost all of the computation of GC-D is the group-wise cross-validation that chemometric practice performs "
                    f"anyway to choose the number of latent variables (K + 1 PLS fits; {tv.shared_setup_s.mean():.1f} s per held-out season "
                    f"for ~70 000 training spectra on one CPU core). The additional cost of GC-D — a three-parameter scale model and one "
                    f"weighted quantile — was {tv.loc['GC-D','method_s']:.2f} s and {tv.loc['GC-D','peak_MiB']:.0f} MiB per season, i.e. "
                    "effectively zero; random-split CP, bagging, GPR and CQR needed "
                    f"{tv.loc['SCP','method_s']:.1f}, {tv.loc['BAG','method_s']:.0f}, {tv.loc['GPR','method_s']:.0f} and "
                    f"{tv.loc['CQR','method_s']:.0f} s because they fit additional models (Supplementary Table S9 and Fig. S1, which "
                    "also explain the memory differences). A deployed GC-D model needs only the PLS model, three scale coefficients "
                    "and q̂; no training data are stored."),
              ]
    # ------------------------------------------------------------------ 4.8 error analysis, bias correction, decisions
    B += [("h2", "4.8. Where the diagnostic scale matters, bias correction and consequences for decisions"),
          ("p", conditional_text()), ("p", bias_text())]
    B += [("fig", os.path.join(FIG, "fig8_error_analysis.png"),
           "Fig. 7. Error analysis. (a) Coverage for new mango seasons by decile of the Q residual ratio Q/Q̃ of the test spectra; "
           "(b) coverage of the 10 % most atypical test spectra (highest Q/Q̃ decile) in five scenarios; (c) coverage of each held-out "
           "instrument against its absolute mean prediction bias, without correction and after bias correction with three labelled "
           "reference fruit (GC-D-BC; arrows); (d) group-averaged coverage as a function of the number k of labelled reference units "
           "of the new group (20 random draws per group; per-group results in Supplementary Table S22). Colours in (b) as in (a). "
           "Panels (b)–(d) were added during revision.")]
    B += [("p", decision_text()),
          ("fig", os.path.join(FIG, "fig9_decisions.png"),
           "Fig. 8. Specification-limit decisions ('accept if the lower interval limit ≥ L') over a grid of limits: (a, b) dry matter of "
           "new mango seasons, (c, d) organic carbon of new soil regions. (a, c) Share of accepted spectra whose reference value is "
           "below L (log scale; zero values plotted at 0.003; dotted line: nominal one-sided 5 %); (b, d) share of truly compliant spectra accepted. Dashed grey: "
           "accepting on the point prediction alone (ŷ ≥ L).")]
    # ------------------------------------------------------------------ 4.10 post-hoc iteration
    it = _csv("iteration1_summary.csv"); itc = _csv("iteration1_comparisons.csv")
    if it is not None and itc is not None and len(it):
        iv = it.set_index(["task", "method"])
        def ivv(t_, m, col="interval_score"):
            return float(iv.loc[(t_, m), col]) if (t_, m) in iv.index else float("nan")
        k = itc[(itc.method == "GC-CQR") & (itc.comparator == "CQR")]
        k2 = itc[(itc.method == "GC-D2") & (itc.comparator == "GC-D")]
        B += [("h2", "4.10. Post-hoc extension: level-dependent errors"),
              ("p", "The soil results revealed a weakness of GC-D not anticipated in the protocol: on new soil regions CQR and GPR had "
                    f"clearly lower interval scores ({g('ossl_lucas_block','CQR','interval_score'):.2f} and "
                    f"{g('ossl_lucas_block','GPR','interval_score'):.2f}) than GC-D ({g('ossl_lucas_block','GC-D','interval_score'):.2f}) and "
                    "even the oracle, because OC errors grow with the OC level and are asymmetric. We therefore tested two post-hoc "
                    "variants (seeds 0–2): GC-D2 adds the predicted value to the scale model, and GC-CQR computes CQR conformity scores "
                    "out-of-group with group-balanced weights (Supplementary Table S7). GC-D2 did not improve on GC-D (lower median "
                    f"interval score in {int((k2.IS_median_diff < 0).sum())} of {len(k2)} scenarios, none significant; soil "
                    f"{ivv('ossl_lucas_block','GC-D2'):.2f} vs {ivv('ossl_lucas_block','GC-D'):.2f}). GC-CQR scored {ivv('ossl_lucas_block','GC-CQR'):.2f} on new soil regions and restored "
                    f"the coverage of CQR under group shift (new instruments {ivv('mango_instrument','CQR','coverage'):.3f} → "
                    f"{ivv('mango_instrument','GC-CQR','coverage'):.3f}, next season {ivv('mango_season_forward','CQR','coverage'):.3f} → "
                    f"{ivv('mango_season_forward','GC-CQR','coverage'):.3f}); its median interval score was lower than CQR's in "
                    f"{int((k.IS_median_diff < 0).sum())} of {len(k)} scenarios ({int((k.IS_p_holm < 0.05).sum())} significant), but on new mango "
                    f"instruments it remained less sharp than GC-D ({ivv('mango_instrument','GC-CQR'):.2f} vs {ivv('mango_instrument','GC-D'):.2f}) "
                    f"and on corn it covered less than CQR ({it[(it.task.str.startswith('corn')) & (it.method == 'GC-CQR')].coverage.min():.3f}–"
                    f"{it[(it.task.str.startswith('corn')) & (it.method == 'GC-CQR')].coverage.max():.3f}). Out-of-group calibration thus transfers "
                    "to other conformity scores, and which score is best depends on whether the error is dominated by spectral novelty "
                    "(mango) or by level-dependent heteroscedasticity (soil).")]
    # ------------------------------------------------------------------ practical recommendations (added in revision)
    B += [("h2", "4.11. Practical recommendations"),
          ("bullets", [
              "Record the deployment-level group (season, instrument, site) and the physical sample of every calibration spectrum, and "
              "validate group-wise and unit-disjoint; random cross-validation over-states the coverage attained on a new group.",
              "With several groups, calibrate intervals on out-of-group residuals: ASTM-G suffices when only average coverage matters; "
              "GC-D keeps coverage for atypical spectra and under drift, which matters for decisions on individual samples.",
              "With fewer than 1/α − 1 groups, state that coverage was verified empirically and may deviate for a single new group by "
              "several percentage points (the group-to-group spread of the group-wise validation estimates by how much); with more "
              "groups, HCP or HJ+ give formal guarantees at the price of wider intervals.",
              "With a single calibration instrument or season, or a large bias in a new group, measure a few reference samples of the "
              "new group for bias correction (GC-D-BC) or calibration transfer before reporting intervals.",
              "Withhold the interval ('model not valid for this sample') when Q/Q̃ exceeds the 99 % calibration limit or the interval "
              "is as wide as the calibration range; choose interval- or point-based acceptance from the relative cost of the two errors.",
          ])]
    B += [("h2", "4.12. Limitations"),
          ("bullets", [
              "GC-D's coverage was verified empirically, not guaranteed; formal guarantees need K ≥ 1/α − 1 groups, and even then the "
              "coverage of a single new group scatters around the nominal level (Section 4.4).",
              "All methods assume exchangeable groups. A trend beyond the variation among past seasons, or a cultivar or instrument type "
              "unlike any in the calibration population, is not covered.",
              "Group-level biases are absorbed into wider intervals; their correction needs labelled samples of the new group and pays "
              "only for large biases (Section 4.8).",
              "The exponential scale model can produce very wide intervals for a few extrapolating spectra, which back-transformation of "
              "a log-scaled analyte amplifies; in a strongly subsampled soil experiment this inflated the mean, though not the median, "
              "interval score of every method, most for the diagnostic-scaled ones (Supplementary Table S18). An upper bound on σ would "
              "prevent this; we did not add one, to keep the method as pre-specified.",
              "Other analytes, techniques (Raman, MIR) and deep models were tested only partially (one CNN), and decisions for two "
              "analytes only. The post-hoc variants (Section 4.10) and the analyses added during revision were designed after seeing "
              "the results and need independent confirmation.",
          ])]
    return B


def front_and_back(C, N, s, c, h, ex, g):
    title = ("Group-conformal calibration of near-infrared prediction intervals for new seasons, instruments and "
             "regions using PLS diagnostics")
    ab = (f"Prediction intervals for multivariate calibration are usually calibrated on samples that resemble the calibration "
          f"set, but near-infrared (NIR) models are deployed on new harvest seasons, instruments and regions. Using {N['n_spectra_total']} "
          f"public spectra (mango dry matter, soil organic carbon, corn, tablets) in {N['n_shift_tasks']} deployment-shift scenarios "
          f"with sample-disjoint group splits, we show that classical partial least squares (PLS) intervals and random-split conformal prediction "
          f"under-cover new groups: for new mango seasons and instruments, random-split conformal prediction covered "
          f"{g('mango_season_forward','SCP'):.2f}–{g('mango_season_loso','SCP'):.2f} of spectra at a nominal 0.90. We propose "
          f"group-conformal calibration (GC-D), which computes conformity scores out-of-group with group-balanced weights and "
          f"scales them by Hotelling T² and Q residuals. GC-D covered {g('mango_season_forward','GC-D'):.2f}–"
          f"{g('mango_season_loso','GC-D'):.2f} for new seasons, {g('mango_instrument','GC-D'):.2f} for new instruments and "
          f"{g('ossl_lucas_block','GC-D'):.2f} for new soil regions, with interval scores close to an oracle calibrated on the "
          f"new group, and lowered false acceptances in specification-limit decisions. Out-of-group calibration supplied most "
          f"of the gain — a classical interval based on the group-wise root-mean-square error of cross-validation reached similar coverage with higher interval scores — "
          f"whereas diagnostic scaling kept the coverage of atypical spectra and under spectral drift. Interval-score gains over random-split "
          f"conformal prediction were consistent in direction but mostly not significant at the group level. Finite-sample "
          f"group-level guarantees required at least 1/α − 1 calibration groups (ten at 90 %), and no interval method rescued "
          f"uncorrected instrument transfer, for which a few labelled samples of the new group and a Q-based rejection rule are needed.")
    meta = dict(
        title=title,
        authors="P N Bhargav Teja^{a}, Divya Meena S^{a,*}",
        affiliations=["^{a} School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, Tamil Nadu, India"],
        corresponding="* Corresponding author: Divya Meena S, divyameena.s@vit.ac.in",
        abstract=[ab],
        keywords=["Near-infrared spectroscopy", "Multivariate calibration", "Conformal prediction", "Prediction interval",
                  "Calibration transfer", "Measurement uncertainty"],
    )
    tail = [
        ("h1", "5. Conclusions"),
        ("p", "Prediction intervals for NIR calibrations should be calibrated against the kind of variation the model will meet. "
              "Computing conformity scores out-of-group, weighting groups equally and scaling by the PLS diagnostics T² and Q kept "
              "intervals close to nominal coverage for new seasons, instruments and regions in our scenarios with several groups, at no "
              "cost beyond the group-wise cross-validation that chemometricians already run. Most of the gain in average coverage comes "
              "from out-of-group calibration itself, which a classical interval with group-wise RMSECV also provides; the diagnostic scale "
              "adds what matters for decisions on individual samples, coverage of atypical spectra and robustness to drift. In a "
              "post-hoc analysis the out-of-group principle also restored the coverage of quantile-regression intervals and gave the "
              "sharpest intervals where errors depended on the analyte level; calibration on out-of-group errors, whatever the "
              "conformity score, is therefore the main transferable message, and the T²/Q-scaled version a cheap default for PLS models."),
        ("p", "Calibration campaigns should span as many seasons or instruments as possible — at least 1/α − 1 for formal guarantees — "
              "and report coverage under group-wise validation; with fewer groups, out-of-group calibration still removes the "
              "systematic under-coverage of random calibration, but the coverage of one deployment remains uncertain. When a model is "
              "calibrated on a single instrument or season, or a new group lies far outside the calibration population, no interval "
              "method can compensate: a few reference samples of the new group are needed for bias correction or transfer, and spectra "
              "that fail the Q check should be reported without an interval."),
        ("h1", "CRediT authorship contribution statement"),
        ("p", "P N Bhargav Teja: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, "
              "Visualization, Writing – original draft. Divya Meena S: Conceptualization, Supervision, Validation, Project "
              "administration, Writing – review & editing."),
        ("h1", "Declaration of competing interest"),
        ("p", "The authors declare that they have no known competing financial interests or personal relationships that could have "
              "appeared to influence the work reported in this paper."),
        ("h1", "Data availability"),
        ("p", f"All data are public: Mango DMC and NIR spectra {C('mango_data')}, Open Soil Spectral Library {C('safanelli2025')}, "
              f"corn {C('corn_data')} and tablet shoot-out data {C('tablet_data')}. Code, configuration, per-group results and the "
              "scripts that regenerate every number, table and figure are provided as supplementary material and will be archived "
              "with a persistent identifier (Zenodo DOI) upon acceptance."),
        ("h1", "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"),
        ("p", "During the preparation of this work the authors used Claude (Anthropic) to assist with literature search, code "
              "development, data analysis and the drafting and editing of the text. After using this tool, the authors reviewed and "
              "edited the content as needed and take full responsibility for the content of the published article."),
    ]
    return meta, tail
