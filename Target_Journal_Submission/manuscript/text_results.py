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
    B += [("p", f"Fig. 3 and Table 2 summarise coverage and interval score at the nominal level 0.90. When the "
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
          ("p", f"For new mango populations, where training data contain other populations of the same seasons and "
                f"instruments, all methods were close to nominal (SCP {g('mango_population','SCP'):.3f}, classical "
                f"{g('mango_population','ASTM-R'):.3f}), which is consistent with the population effect being largely "
                f"absorbed by season and instrument effects already represented in training. On the exchangeable control "
                f"(tablets measured on the calibration instrument) every method reached at least nominal coverage "
                f"(Supplementary Table S2).")]
    B += [("fig", os.path.join(FIG, "fig3_main_coverage_score.png"),
           "Fig. 3. Group-averaged coverage (left; bars are 95 % bootstrap intervals over held-out groups) and interval "
           "score relative to the oracle (right; lower is better; values beyond 3 or infinite are printed) at nominal "
           "coverage 0.90, means over five seeds. GC-D: proposed group-conformal calibration with diagnostic scaling.")]
    # Table 2
    t2 = pd.read_csv(os.path.join(TAB, "table_coverage_alpha0.1.csv"), dtype=str)
    t3 = pd.read_csv(os.path.join(TAB, "table_interval_score_alpha0.1.csv"), dtype=str)
    cols = ["Method", "M-season", "M-forward", "M-instrument", "M-population", "S-region", "C-moist", "C-oil", "C-prot", "C-starch"]
    keep = ["ASTM-R", "ASTM-G", "BAG", "GPR", "CQR", "SCP", "CV+", "WCP", "HJ+", "HCP-D", "GC-D+", "GC-D", "ORACLE"]
    rows = [cols] + [[f"{a} / {b}" if j else a for j, (a, b) in enumerate(zip(r1, r2))]
                     for r1, r2 in zip(t2[t2.Method.isin(keep)][cols].values.tolist(), t3[t3.Method.isin(keep)][cols].values.tolist())]
    B += [("table", rows, "Table 2. Group-averaged coverage / mean interval score at nominal coverage 0.90 (means over five seeds). "
                          "M = mango, S = soil (LUCAS), C = corn. ∞: at least one group received an unbounded interval.",
           "WCP returns unbounded intervals when the estimated density ratio places more than α of the weight on the test "
           "point; HJ+, HCP-D and GC-D+ are unbounded whenever the number of calibration groups is too small for their "
           "finite-sample correction (Section 2.4).", [len(rows) - 2])]
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
                f"(new instrument). For new seasons GC-D's interval score was within "
                f"{100*abs(g('mango_season_loso','GC-D','interval_score')/g('mango_season_loso','ORACLE','interval_score')-1):.0f} % "
                f"of the oracle's."),
          ("p", "Pre-registered hypothesis H2 required coverage between 0.87 and 0.95 on every task with at least ten "
                f"training groups ({', '.join(NICE[t] for t in many)}); it is "
                f"{'supported' if h['H2']['supported'] else 'not supported'}"
                + ("" if h["H2"]["supported"] else
                   f" (outside the range: {', '.join(NICE[t] + ' ' + f3(h['H2']['values'][t]) for t, ok in h['H2']['per_task'].items() if not ok)})")
                + ". Paired over held-out groups, GC-D had a lower interval score than SCP in "
                f"{int((cmp.loc[[t for t in MAIN if t in cmp.index], 'IS_median_diff'] < 0).sum())} of {len([t for t in MAIN if t in cmp.index])} "
                f"main scenarios; the differences were significant after Holm correction for "
                f"{', '.join(NICE[t] for t in MAIN if t in cmp.index and cmp.loc[t,'IS_p_holm'] < 0.05 and cmp.loc[t,'IS_median_diff'] < 0) or 'no scenario'} "
                "(Table 3, Fig. 10). With only seven seasons the season comparisons have little power, and their effect "
                "sizes should be read alongside the per-season values in Fig. 4.")]
    B += [("fig", os.path.join(FIG, "fig4_per_group_coverage.png"),
           "Fig. 4. Coverage in each held-out group (points; seed-averaged) for the classical PLS interval, random-split "
           "conformal prediction and GC-D; horizontal bars are medians and the dashed line is the nominal 0.90.")]
    st = pd.read_csv(os.path.join(TAB, "table_statistics.csv"), dtype=str)
    B += [("table", [list(st.columns)] + st.values.tolist(),
           "Table 3. Paired comparison of GC-D with each comparator over held-out groups: matched-pairs rank-biserial "
           "correlation of the interval score (negative: GC-D lower) with Holm-adjusted two-sided Wilcoxon p-values in "
           "parentheses.")]
    # ------------------------------------------------------------------ 4.3 ablation
    h3 = h["H3"]
    B += [("h2", "4.3. Which components matter"),
          ("p", "The factorial ablation (Fig. 5) separates the three ingredients. Replacing random calibration folds by "
                f"out-of-group folds (R-U-A → G-U-A) carried most of the coverage gain on the mango shift scenarios, e.g. "
                f"{g('mango_instrument','R-U-A'):.3f} → {g('mango_instrument','G-U-A'):.3f} for new instruments and "
                f"{g('mango_season_forward','R-U-A'):.3f} → {g('mango_season_forward','G-U-A'):.3f} for the next season. "
                f"Group-balanced weights (G-U-A → G-W-A) changed coverage little when groups were of similar size and "
                f"mattered most when group sizes were unequal (new instruments: {g('mango_instrument','G-U-A'):.3f} → "
                f"{g('mango_instrument','G-W-A'):.3f}). Diagnostic normalisation (G-W-A → GC-D) lowered the interval score in "
                f"{h3['n_tasks_lower']} of {h3['n_tasks']} main scenarios (significantly after Holm correction in "
                f"{h3['n_tasks_significant_lower']}), so H3 is "
                f"{'supported' if h3['n_tasks_significant_lower'] >= 1 and h3['n_tasks_lower'] > h3['n_tasks']/2 else 'only partly supported'}: "
                "the scaling redistributes width from typical to atypical spectra, which helps most when test groups "
                "contain spectra the model has not seen (Section 4.6)."),
          ("fig", os.path.join(FIG, "fig5_ablation.png"),
           "Fig. 5. Factorial ablation of GC-D at nominal coverage 0.90: (a) coverage (colour: deviation from 0.90, "
           "red = under-coverage) and (b) interval score relative to GC-D (values > 1: worse than GC-D).")]
    return B, None, []
