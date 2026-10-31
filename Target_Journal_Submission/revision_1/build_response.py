"""Point-by-point response to the reviewers (TAL-D-26-07648, revision 1).

Every comment is quoted verbatim from reviewer_comments.json (extracted from the decision letter); every number is read
from the result files that the revised manuscript uses. Writes Response_to_Reviewers.docx and response_to_reviewers.md
(plain text for pasting into the journal's peer-review platform)."""
import json, os
import numpy as np, pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, "code", "results"); RV = os.path.join(R, "revision")
rd = lambda f, d=RV: pd.read_csv(os.path.join(d, f))
CM = json.load(open(os.path.join(HERE, "reviewer_comments.json")))

# ------------------------------------------------------------------------------------------------ numbers
s = rd("summary_results.csv", R); s = s[s.alpha == 0.1]
g = lambda t, m, c="coverage": float(s[(s.task == t) & (s.method == m)][c].iloc[0])
v1 = json.load(open(os.path.join(HERE, "submitted_v1_content.json")))
v2 = json.load(open(os.path.join(ROOT, "manuscript", "Final_Manuscript_content.json")))
words = lambda c: sum(len((b.get("text", "") + " " + " ".join(b.get("items", []))).split()) for b in c["blocks"] if b["type"] in ("p", "bullets"))
W1, W2 = words(v1), words(v2)
pe = rd("population_error_comparison.csv").set_index("scenario")
pa = json.load(open(os.path.join(RV, "population_absorption.json")))
es = rd("effect_size_intervals.csv"); esS = es[es.comparator == "SCP"].set_index("task")
MANY = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block"]
CORN = ["corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
cc = rd("conditional_coverage.csv"); cc = cc[cc.by == "Qr"]
ccv = lambda t, m, d: float(cc[(cc.task == t) & (cc.method == m) & (cc.decile == d)].coverage.iloc[0])
T4 = ["mango_season_loso", "mango_season_forward", "mango_instrument", "ossl_lucas_block"]
sf = rd("scale_form_summary.csv"); base = "default (Poisson, log(1+T²), Q/Q̃)"
sfv = sf.set_index(["task", "variant"]); alt = sf[~sf.variant.isin([base, "Q only", "T² only"])]
dcov = max(abs(r.coverage - sfv.loc[(r.task, base), "coverage"]) for r in alt.itertuples())
dis = [r.interval_score / sfv.loc[(r.task, base), "interval_score"] - 1 for r in alt.itertuples()]
qn_same = all(abs(r.interval_score - sfv.loc[(r.task, base), "interval_score"]) < 1e-6 for r in sf[sf.variant == "Q not normalised by Q̃"].itertuples())
ub = rd("unbalanced_summary.csv").set_index(["task", "method"])
bs = rd("bias_correction_summary.csv").set_index(["task", "variant", "k"])
N0, SH, BC = "GC-D (no correction)", "GC-D, centre shifted", "GC-D-BC (shifted and recalibrated)"
bq = lambda t, v, k, c="coverage": float(bs.loc[(t, v, k), c])
bpg = rd("bias_correction_per_group.csv"); bpg = bpg.assign(gk=pd.to_numeric(bpg.group, errors="coerce"))
p114 = bpg[(bpg.task == "mango_population") & (bpg.gk == 114500.0)].set_index(["variant", "k"])
rj = rd("rejection_rule.csv"); rq = rj[rj.rule == "rej_Q99"].set_index(["perturbation", "level"]); rq95 = rj[rj.rule == "rej_Q95"].set_index(["perturbation", "level"])
un = rd("uninformative_rule.csv").set_index(["task", "rule"])
dec = rd("decisions_grid.csv"); dm = dec[dec.task == "mango_season_loso"].set_index(["method", "L"]); ds = dec[dec.task == "ossl_lucas_block"].set_index(["method", "L"])
be = rd("decisions_break_even.csv"); beS = be[(be.task == "mango_season_loso") & (be.comparator == "SCP")].set_index("L").break_even_cost_ratio
sim = rd("simulation_finiteK.csv"); simG = sim[(sim.method == "GC-A") & (sim.tau == 1.0)]; simS = sim[(sim.method == "SCP") & (sim.tau == 1.0)]
fin = sim[(sim.method == "GC-A+") & (sim.finite_frac >= 0.99)].groupby("alpha").K.min()
disp = rd("coverage_dispersion.csv"); dG = disp[disp.method == "GC-D"].set_index("task")
wv = rd("wcp_variants_summary.csv"); wv["cap"] = wv["cap"].astype(str)
w0 = wv[wv.estimator.str.startswith("logistic, C = 1, all") & (wv.cap == "none")].set_index("task")
w3 = wv[wv.estimator.str.contains("first 3") & (wv.cap == "none") & wv.task.str.startswith("mango")]
wr = wv[wv.estimator.str.startswith("logistic, C = 0.01") & (wv.cap == "none")]
wcap = wv[wv.estimator.str.startswith("logistic, C = 1, all") & (wv.cap != "none") & wv.task.str.startswith("mango")]
wcapS = wv[wv.estimator.str.startswith("logistic, C = 1, all") & (wv.cap != "none") & (wv.task == "ossl_lucas_block")]
wc = rd("wcp_clip_summary.csv", R); wcv = wc[wc.method == "WCP-clip"].set_index("task")
al = rd("alpha_consistency.csv"); alM = al[al.task.isin(["mango_season_loso", "mango_season_forward", "mango_instrument"])]
tm = rd("timing_summary.csv", R).set_index("method")
upg = rd("units_per_group.csv").set_index("task")
pgr = rd("per_group_results.csv", R); pgr = pgr[(pgr.alpha == 0.1)]
gd = pgr[(pgr.task == "mango_instrument") & (pgr.method == "GC-D")]
cmp_ = rd("comparisons_alpha0.1.csv", R).set_index(["task", "comparator"])
h3 = json.load(open(os.path.join(R, "hypotheses.json")))["H3"]
tab_lim = rd("diag_limits_tablets.csv").set_index("fold")
tp = pd.read_parquet(os.path.join(R, "main", "points_tablets_seed0.parquet")); tp = tp[(tp.method == "GC-D") & (tp.alpha == 0.1)]
tab_fl = (tp.Qr > tp.fold.map(tab_lim.Qr99)).groupby(tp.group).mean()
f3 = lambda x: f"{x:.3f}"
pct = lambda x, d=0: f"{100*x:.{d}f} %"
pm = lambda x: f"{x:+.1f}".replace("-", "−")

# ------------------------------------------------------------------------------------------------ responses
R1 = {
1: ("We agree that this needed to be stated explicitly. The coverage theory (Dunn et al.; Lee et al.) is borrowed and is not "
    "our contribution. The distinction is the adaptation to multivariate calibration, where three features of NIR practice are not "
    "covered by generic hierarchical data: (i) groups and physical samples are crossed (the same fruit or corn sample is scanned on "
    "several instruments), so the calibration must be unit-disjoint as well as group-disjoint, which generic leave-one-group-out "
    "schemes do not ensure; (ii) the PLS model's own diagnostics T² and Q describe the position of a new spectrum relative to the "
    "calibration space and can drive the interval width without a separate difficulty model; (iii) out-of-group residuals are a "
    "by-product of the group-wise cross-validation already used to select the number of latent variables, while the number of groups "
    "is typically small — exactly where the finite-sample guarantees of the hierarchical methods break down. The answer is therefore "
    "both: the problem setting (NIR group structures with crossed units and few groups) and the technical adaptation (PLS diagnostics, "
    "unit-disjoint cross-fitting, re-use of the group-wise cross-validation), together with the empirical evidence of how large the "
    "coverage loss of current practice is.",
    "New paragraph in the Introduction ('What distinguishes this work …'); contribution list revised."),
2: ("Thank you; we moved the statement of what is borrowed and what is new to the Introduction, immediately after the paragraph "
    "on the distinction (comment 1), and removed the former Section 4.9, whose remaining content (complementarity with calibration "
    "transfer) is now part of Sections 4.6 and 5.",
    "Introduction, paragraph 'We state at the outset what is borrowed …'; former Section 4.9 removed (sections renumbered)."),
3: ("Papadopoulos et al. (2011) normalise the residual by a non-parametric difficulty estimate, the average error (or distance) of "
    "the k nearest training points, fitted on a proper training set and calibrated on a random split; the same idea underlies the "
    "normalised inductive conformal predictor used for mid-infrared food adulteration (Jović et al.). Our σ(x) differs in two "
    "respects: it is a three-parameter parametric function of T² and Q, which extrapolates to spectra unlike any training spectrum "
    "(where nearest neighbours carry no information about the new region of the space), and it is fitted to out-of-group residuals, so "
    "it learns how the error grows when a spectrum comes from a group the model has not seen. A k-nearest-neighbour normalised predictor "
    f"(NCP-kNN) was already included as a baseline; it under-covered the mango shift scenarios like SCP (new instruments "
    f"{f3(g('mango_instrument','NCP-kNN'))} at nominal 0.90; Supplementary Tables S3, S4 and S14).",
    "Introduction, paragraph 'We state at the outset what is borrowed …'."),
4: ("We added the explanation to the Methods and an analysis of its cause to the Results. WCP places the weight "
    "w(x)/(Σwᵢ + w(x)) of the test spectrum at +∞, so the interval is unbounded whenever this share exceeds α. With seed 0, a logistic "
    f"classifier separated calibration and deployment spectra with AUC {w0.clf_auc.min():.2f}–{w0.clf_auc.max():.2f}; the effective sample "
    f"size of the calibration weights fell to {pct(w0.ess_frac.min(),1)}–{pct(w0.ess_frac.max())} of the calibration set; and for new "
    f"instruments {pct(w0.test_mass_gt_alpha.max())} of the deployment spectra carried more than α of the total weight. To separate a "
    "methodological from an estimator limitation, we repeated WCP with two other density-ratio estimators and with caps of 5–100 on the "
    "normalised ratios (new Table S20). A strongly regularised classifier (C = 0.01) still left up to "
    f"{pct(1 - wr.finite_frac.min())} of the intervals unbounded. A classifier restricted to three PLS scores produced bounded intervals but no "
    f"longer separated the groups (AUC {w3.clf_auc.min():.2f}–{w3.clf_auc.max():.2f}), so it hardly reweighted and covered only "
    f"{f3(w3.coverage.min())}–{f3(w3.coverage.max())} on the mango shifts, like SCP. Caps of 5–100 gave coverage of "
    f"{f3(wcap.coverage.min())}–{f3(wcap.coverage.max())} on the mango shifts (and {f3(wcapS.coverage.min())}–{f3(wcapS.coverage.max())} "
    "on the milder soil-region shift). Our reading is that the failure is intrinsic to covariate-shift weighting when "
    "calibration and deployment spectra barely overlap: an estimator that captures the shift produces extreme weights, and one that "
    "avoids extreme weights does not correct for the shift. With the ~30 calibration spectra of the corn scenarios, even a capped weight "
    "exceeds α of the total (a small-sample limitation).",
    "Section 3.3 (mechanism), Section 4.1 (analysis), Supplementary Table S20 (new)."),
5: ("We agree and now address this directly. Out-of-group calibration without scaling (G-W-A), and therefore ASTM-G, achieves near-"
    "nominal coverage averaged over all spectra, but it gives every spectrum of a group the same width (ASTM-G varies the width only "
    "through the leverage). It thus over-covers typical spectra and under-covers atypical ones. Systematically across scenarios "
    f"(new Fig. 7b, Table S21), G-W-A covered {f3(min(ccv(t,'G-W-A',1) for t in T4))}–{f3(max(ccv(t,'G-W-A',1) for t in T4))} of "
    f"the spectra in the lowest Q/Q̃ decile, but only {f3(min(ccv(t,'G-W-A',10) for t in T4))}–{f3(max(ccv(t,'G-W-A',10) for t in T4))} "
    f"in the highest decile of the new-season, next-season, new-instrument and soil-region scenarios, and ASTM-G covered "
    f"{f3(min(ccv(t,'ASTM-G',10) for t in T4))}–{f3(max(ccv(t,'ASTM-G',10) for t in T4))}; GC-D covered "
    f"{f3(min(ccv(t,'GC-D',10) for t in T4))}–{f3(max(ccv(t,'GC-D',10) for t in T4))}. In the KSSL → LUCAS transfer the highest decile "
    f"was covered {f3(ccv('ossl_kssl_to_lucas','G-W-A',10))} by G-W-A and {f3(ccv('ossl_kssl_to_lucas','GC-D',10))} by GC-D, and under a "
    "2-nm wavelength shift G-W-A fell to 0.846 while GC-D covered 0.938 (Fig. 6c). The scaling is therefore irreplaceable whenever "
    "decisions are taken on individual samples, some of which are atypical — the typical situation after a change of season, "
    "instrument or region — whereas ASTM-G suffices if only the average coverage matters. We say this explicitly in Sections 4.3, 4.8 "
    "and 4.10 and in the Conclusions.",
    "Section 4.3 (last sentences), Section 4.8 (first paragraph), Fig. 7a,b, Supplementary Table S21 (new), Section 4.10, Conclusions."),
6: ("We agree and have strengthened this in the Conclusions: calibration on out-of-group errors, whatever the conformity score, is "
    "now presented as the main transferable message, with the T²/Q-scaled version as a cheap default for PLS models. Because GC-CQR was "
    "designed after seeing the soil results and evaluated on the same data, we keep it labelled as post-hoc and requiring independent "
    "confirmation, and we report its weaknesses (less sharp than GC-D on new mango instruments; lower coverage than CQR on corn).",
    "Conclusions, first paragraph; Section 4.9 (post-hoc) condensed."),
7: ("Yes: repeated measurement of the same physical samples across groups occurs only where groups are instruments. In the "
    f"instrument scenario, {int(upg.loc['mango_instrument','units_in_more_than_one_group']):,} of the "
    f"{int(upg.loc['mango_instrument','units']):,} fruit measured on the {int(upg.loc['mango_instrument','held_out_groups'])} held-out "
    "instruments were measured on more than one of them, and every corn and tablet sample was measured on every instrument; seasons, "
    "populations and soil regions share no units. The new Supplementary Table S16 lists, for every scenario, the number of held-out "
    "groups, spectra, physical units, units per group (median, minimum, maximum), units occurring in more than one group, and the range "
    "of calibration groups per outer fold. Every unit shared with a held-out group is removed from the training data of every model "
    "that predicts any of its spectra (asserted in the code for every outer and inner split).",
    "Section 3.2 (new paragraph), Supplementary Table S16 (new)."),
8: ("We performed the suggested semi-synthetic experiment. In every outer fold of the new-instrument, new-season and soil-region "
    "scenarios, the training groups were subsampled to Zipf-like sizes (relative sizes 1, 2^−1.5, 3^−1.5, … in random order; three "
    "repetitions), so that the largest group held "
    f"{pct(ub.xs('GC-D', level='method').largest_share.min())}–{pct(ub.xs('GC-D', level='method').largest_share.max())} of the "
    "training spectra and the largest-to-smallest ratio was up to "
    f"{ub.xs('GC-D', level='method').max_min_ratio.max():.0f}. Group-balanced weights then raised the coverage of the diagnostic-scaled "
    f"interval from {f3(ub.loc[('mango_instrument','G-U-D'),'coverage'])} to {f3(ub.loc[('mango_instrument','GC-D'),'coverage'])} (new "
    f"instruments), from {f3(ub.loc[('mango_season_loso','G-U-D'),'coverage'])} to {f3(ub.loc[('mango_season_loso','GC-D'),'coverage'])} "
    f"(new seasons) and from {f3(ub.loc[('ossl_lucas_block','G-U-D'),'coverage'])} to {f3(ub.loc[('ossl_lucas_block','GC-D'),'coverage'])} "
    "(soil regions), and similarly for absolute scores; with uniform weights the calibration reflects mainly the error of the largest "
    "group. The experiment also revealed a weakness that we now report as a limitation: with only ~3,000 training spectra, a few "
    "extrapolating organic-rich soil samples received extremely wide back-transformed intervals for every method, most for the "
    "diagnostic-scaled ones, which inflated the mean (not the median) interval score (Table S18).",
    "Section 4.3, Supplementary Table S18 (new), Section 4.11 (limitation added)."),
9: ("We added this sensitivity analysis (new Table S17): Gamma and Gaussian log-link GLMs, least squares on log|r| (log-normal), "
    "log T² instead of log(1 + T²), Q not normalised by Q̃, a T² × Q interaction term, a fit weighted by the group-balanced weights, and "
    "either diagnostic alone, for the new-season, next-season, new-instrument and soil-region scenarios. The alternatives changed the "
    f"group-averaged coverage of GC-D by at most {dcov:.3f} and its interval score by {pm(100*min(dis))} to {pm(100*max(dis))} %"
    + ("; omitting the normalisation of Q gave identical intervals, as expected because it only shifts the intercept. " if qn_same else ". ")
    + "The choice of the Poisson quasi-likelihood is now motivated in Section 2.3 (consistent estimation of the mean of |r| under a log "
    "link whatever the distribution of the residuals; Gourieroux, Monfort & Trognon 1984).",
    "Section 2.3 (justification), Section 4.5, Supplementary Table S17 (new), reference added."),
10: ("Thank you for pointing this out. The protocol stated H3 as a direction without a decision rule (unlike H1 and H2, which have "
     "explicit thresholds). We now state the rule that we apply, and say openly that it was formulated during the revision, after the "
     "results were known: H3 is supported when GC-D has the lower interval score in most main scenarios with Holm-significant "
     "differences in most, partly supported when only the first condition holds, and not supported otherwise. With "
     f"{h3['n_tasks_lower']} of {h3['n_tasks']} scenarios lower and {h3['n_tasks_significant_lower']} significant, H3 is partly supported, "
     "as reported in the submitted version. We also explain that the average interval score is not where the scaling matters "
     "(see comment 5).",
     "Section 3.4; Section 4.3."),
11: ("We agree that the explanation lacked direct support, and on testing it we found it only partly correct, so we replaced it. "
     "Direct evidence that a new population brings little extra error: its RMSEP was only "
     f"{pct(pe.loc['new population','ratio_to_random_cv']-1)} above the random unit-wise cross-validation error of the same data, against "
     f"{pct(pe.loc['new season','ratio_to_random_cv']-1)} for a new season and {pct(pe.loc['new instrument','ratio_to_random_cv']-1)} for a "
     "new instrument (new Table S27a). In the PLS latent space, however, populations are not simply relabelled seasons and instruments: "
     f"season and instrument composition explained {pct(pa['r2_pop_mean_scores_by_season_and_instruments'])} of the between-population "
     f"variance of the population-mean scores (season alone {pct(pa['r2_pop_mean_scores_by_season'])}), and season explained "
     f"{pct(pa['r2_season_of_pop_residual_means_population'])} of the variance of the population-mean residuals (Table S27b). The revised "
     "text therefore says that the model generalises across lots, rather than that population effects are absorbed by season and "
     "instrument effects.",
     "Section 4.1 (third paragraph), Supplementary Table S27 (new)."),
12: ("Agreed. Section 4.7 now states that almost all of the computation of GC-D is the group-wise cross-validation (K + 1 PLS fits) "
     "that chemometric practice performs anyway to choose the number of latent variables, so that the additional cost of GC-D "
     f"({tm.loc['GC-D','method_s']:.2f} s and {tm.loc['GC-D','peak_MiB']:.0f} MiB per held-out season) is effectively zero; the section was "
     "shortened at the same time (comment 23).",
     "Section 4.7."),
13: ("We annotated population 114500 in Fig. 4 and extended the discussion in Section 4.8. Its fruit were green 'Kensington Pride' of 2020, harvested before maturity, with a mean DM far below "
     "that of the other lots, which the model over-predicted by 3.3 % DM; no calibration of interval width can repair such a bias. "
     "Following the suggestion, we tested labelled samples of the new group (comment 17): with a single labelled fruit, the "
     f"bias-corrected and recalibrated interval (GC-D-BC) covered {f3(p114.loc[(BC,1),'coverage'])} of this population's spectra, against "
     f"{f3(p114.loc[(N0,1),'coverage'])} without correction. We now recommend a few reference samples of a new group whenever a large "
     "group-level bias is plausible (Section 4.10).",
     "Fig. 4 (annotation), Section 4.8, Fig. 7d, Section 4.10."),
14: ("We now acknowledge the limitation explicitly in Section 3.4 and complement the tests by estimation (new Table S19): mean "
     "differences in interval score with 95 % bootstrap confidence intervals over the units of analysis, and posterior probabilities "
     "that GC-D has the lower mean interval score under the Bayesian bootstrap (Rubin 1981). Relative to SCP, GC-D lowered the mean "
     f"interval score by {-100*esS.loc[MANY,'rel_mean_diff'].max():.0f}–{-100*esS.loc[MANY,'rel_mean_diff'].min():.0f} % in the mango and "
     "soil scenarios; the bootstrap interval excluded zero for new instruments, new populations and new soil regions; and the posterior "
     f"probability was {esS.loc[MANY,'post_prob_gcd_lower'].min():.2f}–{esS.loc[MANY,'post_prob_gcd_lower'].max():.2f} (corn "
     f"{esS.loc[CORN,'post_prob_gcd_lower'].min():.2f}–{esS.loc[CORN,'post_prob_gcd_lower'].max():.2f}, i.e. no consistent advantage). We "
     "recommend judging a calibration method with few groups by such estimates together with the coverage it attains, rather than by a "
     "test on five to seven groups (Section 4.2).",
     "Section 3.4, Section 4.2, Supplementary Table S19 (new), reference added."),
15: ("We added concrete recommendations. With a model calibrated on a single instrument or season, no interval method can anticipate "
     "the error of a new one, and reporting a severely under-covering interval is misleading. We therefore propose two checks computed "
     "from the calibration data alone, after which the analyst should report 'no reliable interval — model not valid for this sample': "
     "(i) the interval is at least as wide as the central 90 % range of the training reference values, or (ii) Q/Q̃ exceeds the 99 % "
     "quantile of the out-of-group calibration values. At least one check fired for "
     f"{pct(min(un.loc[(t,'either'),'share_flagged'] for t in CORN))}–{pct(max(un.loc[(t,'either'),'share_flagged'] for t in CORN))} "
     f"of the corn test spectra and {pct(un.loc[('ossl_kssl_to_lucas','either'),'share_flagged'])} of the KSSL → LUCAS spectra, against "
     f"{pct(min(un.loc[(t,'either'),'share_flagged'] for t in ['mango_season_loso','mango_instrument','ossl_lucas_block']),1)}–"
     f"{pct(max(un.loc[(t,'either'),'share_flagged'] for t in ['mango_season_loso','mango_instrument','ossl_lucas_block']),1)} in the "
     "mango and soil-region scenarios; for the tablets, which were calibrated on one instrument, the Q check flagged "
     f"{pct(tab_fl.get('inst2'))} of the second-instrument spectra and {pct(tab_fl.get('inst1'),1)} of the calibration-instrument "
     "spectra. When a check fires for a large share of a new instrument's spectra, the model should be transferred or recalibrated with "
     "a few reference samples (bias correction, comment 17).",
     "Section 4.6 (new paragraph), Section 4.10, Conclusions, Supplementary Table S24 (new)."),
16: ("We extended the decision analysis in Section 4.8 to a grid of limits "
     "(12–19 % DM) and to soil organic carbon (1–8 % OC), and we added a cost analysis (new Fig. 8, Tables S25a,b). With c the cost of "
     "accepting a non-compliant item relative to rejecting a compliant one, GC-D has a lower expected cost than SCP for c above "
     f"{beS.loc[16.0]:.1f} at L = 16 % DM ({beS.min():.1f}–{beS.max():.1f} over the grid). We discuss the decision contexts: contractual "
     "penalties for out-of-specification lots, minimum-maturity rules or safety-related attributes (c ≫ 10) favour GC-D, whereas bulk "
     "processing in which a rejected fruit is merely downgraded (c ≈ 1) favours accepting on the point prediction. The point-prediction "
     f"rule kept {f3(dm.loc[('GC-D',16.0),'point_rule_yield'])} of the compliant fruit at L = 16 %, but "
     f"{f3(dm.loc[('GC-D',16.0),'point_rule_false_acceptance'])} of the accepted fruit were non-compliant.",
     "Section 4.8 (last paragraph), Fig. 8 (revised), Supplementary Table S25 (new)."),
17: ("A clarification first: the worst new-instrument coverage of GC-D in Table S4a is "
     f"{f3(gd.groupby('group').coverage.mean().min())}; 0.447 is the value of GC-D+ (the variant with the finite-sample correction). We "
     "performed the suggested analysis: k = 1, 2, 3, 5 and 10 labelled fruit of the new instrument (20 random draws per instrument), used "
     "(a) to shift the interval centre by their mean residual, and (b) in a recalibrated variant (GC-D-BC) that mimics the same correction "
     "in every calibration group before the scale model and q̂ are fitted, so that the calibration accounts for the noise of the bias "
     f"estimate. Shifting with three fruit raised the worst-instrument coverage from {f3(bq('mango_instrument',N0,3,'worst_group'))} to "
     f"{f3(bq('mango_instrument',SH,3,'worst_group'))}, but with one fruit the noisy estimate lowered the group-averaged coverage to "
     f"{f3(bq('mango_instrument',SH,1))}, and with more fruit the shifted intervals over-covered ({f3(bq('mango_instrument',SH,10))} at "
     "k = 10). GC-D-BC kept the average coverage at "
     f"{f3(min(bq('mango_instrument',BC,k) for k in (1,2,3,5,10)))}–{f3(max(bq('mango_instrument',BC,k) for k in (1,2,3,5,10)))} for every "
     f"k while narrowing the intervals (interval score {bq('mango_instrument',BC,3,'interval_score'):.2f} vs "
     f"{bq('mango_instrument',N0,3,'interval_score'):.2f} at k = 3; worst instrument {f3(bq('mango_instrument',BC,3,'worst_group'))}). For "
     "new seasons, whose biases are small relative to the fruit-to-fruit variation, a few fruit did not help (Section 4.8). Bias "
     "correction therefore pays for large group-level biases and should be calibrated as in GC-D-BC.",
     "Section 4.8 (second paragraph), Fig. 7c,d (new), Supplementary Table S22 (new), Section 4.10."),
18: ("We designed and evaluated such a rule: withhold the interval when Q/Q̃ exceeds the 95 % or 99 % quantile of the out-of-group "
     "calibration values (computed from the training data alone), optionally also when T² exceeds its 99 % quantile. On the perturbed "
     "new-season spectra (new Table S23), the 99 % rule rejected "
     f"{pct(rq.loc[('none',0.0),'rejected'],1)} of the unperturbed spectra (false positives; {pct(rq95.loc[('none',0.0),'rejected'],1)} with "
     f"the 95 % rule), {pct(rq.loc[('noise',0.01),'rejected'])} of the spectra with 1 % noise and {pct(rq.loc[('noise',0.03),'rejected'])} "
     f"with 3 % noise. Its false negatives were perturbations that hardly change Q (0.3 % noise: {pct(rq.loc[('noise',0.003),'rejected'])} "
     "rejected; gain and baseline tilt, which the derivative preprocessing removes; shifts of 0.5–1 nm), which GC-D covered at least "
     f"{f3(min(rq.loc[k_,'coverage_all'] for k_ in [('noise',0.003),('gain',0.05),('offset_slope',2.0),('wl_shift',0.5),('wl_shift',1.0)]))} "
     f"anyway. We also report its limit: the retained 1 %-noise spectra were covered only {f3(rq.loc[('noise',0.01),'coverage_retained'])}, "
     f"and the stricter 95 % rule rejected {pct(rq95.loc[('noise',0.01),'rejected'])} of them at the price of more false rejections.",
     "Section 4.5, Supplementary Table S23 (new), Section 4.10."),
19: ("This is an important practical point. We now (i) state in Section 2.4 and Section 4.4 that the threshold for formal guarantees "
     "is K ≥ 1/α − 1 and therefore depends on the nominal level (ten groups at 90 %, twenty at 95 %, five at 80 %); (ii) quantify, with real "
     "data and a new synthetic study (Fig. S3, Table S26), what GC-D delivers with few groups: on average it removes the systematic "
     f"under-coverage of random calibration for every K from 3 to 50 (α = 0.10: {f3(simG[simG.alpha==0.1].mean_coverage.min())}–"
     f"{f3(simG[simG.alpha==0.1].mean_coverage.max())} vs {f3(simS[(simS.alpha==0.1)&(simS.K==3)].mean_coverage.mean())} for random "
     "calibration at K = 3), but the coverage of one deployment remains uncertain by several percentage points; (iii) recommend how to "
     "communicate this 'benefit without guarantee' (Section 4.10): report that coverage was verified empirically and may deviate for a "
     "single new group, using the group-to-group spread of the group-wise validation as the measure. For a single-season crop or a "
     "single-instrument laboratory, no interval method can anticipate the error of a new season or instrument; we recommend a few "
     "reference samples of the new group (comment 17) and the checks of comment 15.",
     "Sections 2.4, 4.4, 4.10, Conclusions; Supplementary Section S26 and Fig. S3 (new)."),
20: ("We will deposit the code, configuration and result files in Zenodo, and the Data availability statement says so. A DOI can be "
     "inserted when the archive is created; we will add it at the proof stage if it is not yet available at resubmission.",
     "Data availability."),
21: ("ORACLE needs no additional model: it computes quantiles of residuals of the final model, which already exist, on the "
     "test group. GC-D needs about 83 MiB because it evaluates T² and Q of every training spectrum under its out-of-group fold model, "
     "which requires reconstructing the n × p training matrix in double precision (≈ 70 000 × 103 × 8 bytes ≈ 58 MB) plus the scale-model "
     "fit. We added a note to Table S9 that explains the memory of every method family (residual sorting only; out-of-fold diagnostics; "
     "an additional PLS fit; a second cross-validation; the GPR kernel matrix; 25 bagged models).",
     "Supplementary Table S9 (note added)."),
22: ("The advantage is consistent across nominal levels. On the mango season and instrument scenarios GC-D covered "
     f"{100*alM.gcd_minus_scp.min():.0f}–{100*alM.gcd_minus_scp.max():.0f} percentage points more than SCP at 0.80, 0.90 and 0.95, the "
     "difference has the same sign at all three levels in every mango and soil scenario, and the group-averaged coverage of GC-D deviated "
     f"from the nominal level by at most {(alM['GC-D'] - alM.nominal).abs().max():.3f}. This is now stated in Section 4.2 and in the note "
     "to Table S3.",
     "Section 4.2 (end of second paragraph); Supplementary Table S3 (note)."),
23: (f"We moved Table 4 to the Supplementary Material (it is a subset of Table S14), the sensitivity details to Table S5/S17, the "
     "computational details to Table S9, and the former Section 4.9 to the Introduction, and we condensed Sections 4.5–4.7 and 4.9. The "
     "additional analyses requested by both reviewers (29 points) could not be added without some text, but we kept their details in "
     f"the Supplementary Material (new Sections S16–S28). The main text now has {W2:,} words of body text against {W1:,} in the submitted "
     "version, three tables instead of four and the same eight figures.",
     "Throughout; Table 4 → Supplementary Table S14; Supplementary Sections S16–S28."),
24: ("Fig. 5 now frames the GC-D column (= G-W-D) in both panels and labels it as the reference. In Fig. 6c the perturbation levels are "
     "shown as short horizontal tick labels grouped under the perturbation type (none, gain, tilt, λ shift, noise), and the panel was "
     "widened.",
     "Fig. 5, Fig. 6c."),
}
R4 = {
1: ("We added both requested analyses. (i) Variance decomposition in the real data: the coverage of GC-D in individual held-out groups "
    f"had a standard deviation of {dG.sd_group_coverage.min():.2f}–{dG.sd_group_coverage.max():.2f}, of which "
    f"{pct(dG.between_group_share.min())}–{pct(dG.between_group_share.max())} was between-group variation and the remainder the "
    "sampling variation of a coverage proportion (new Table S28). (ii) A synthetic hierarchical study (Supplementary Section S26, Fig. S3, "
    "Table S26) of the coverage attained in a single new group for K = 3–50, α = 0.05, 0.10 and 0.20 and balanced or log-normally "
    "distributed group sizes: out-of-group calibration was close to nominal on average for every K, but the standard deviation of "
    f"single-deployment coverage fell only from {simG[(simG.alpha==0.1)&(simG.K==3)].sd_coverage.mean():.2f} (K = 3) to "
    f"{simG[(simG.alpha==0.1)&(simG.K==50)].sd_coverage.mean():.2f} (K = 50) at α = 0.10, because it is caused by the new group's own "
    "effect, which only information about that group can remove. As the reviewer anticipated, the 'about ten groups' threshold is "
    "specific to α = 0.10: the finite-sample correction became finite at K = "
    + ", ".join(f"{int(fin.loc[a_])} for α = {a_:.2f}" for a_ in sorted(fin.index))
    + ", i.e. at K ≥ 1/α − 1, for balanced and unbalanced group sizes alike. The recommendation is qualified accordingly in Sections "
    "2.4, 4.4, 4.10 and 5 and in the abstract.",
    "Sections 2.4 and 4.4 (new paragraph), 4.10, 4.11, Conclusions, Abstract; Supplementary Tables S26 and S28 and Fig. S3 (new)."),
2: ("We agree with this framing and adopted it. Section 4.6 now states that in the corn and KSSL → LUCAS settings the failure is that "
    "of the point predictor, not of the calibration principle: an interval can only quantify the error of a model that is still valid "
    "for the new group, and model transfer or bias correction must precede uncertainty quantification. We also added the decision-"
    "theoretic element: two checks computed from the calibration data (interval as wide as the range of the calibration reference "
    "values; Q/Q̃ above the 99 % calibration quantile) define when an interval should be reported as uninformative ('model not valid for "
    f"this sample'). They fired for {pct(min(un.loc[(t,'either'),'share_flagged'] for t in CORN))}–"
    f"{pct(max(un.loc[(t,'either'),'share_flagged'] for t in CORN))} of the corn spectra and "
    f"{pct(un.loc[('ossl_kssl_to_lucas','either'),'share_flagged'])} of the KSSL → LUCAS spectra, but for at most "
    f"{pct(max(un.loc[(t,'either'),'share_flagged'] for t in ['mango_season_loso','mango_instrument','ossl_lucas_block']),1)} in the "
    "mango and soil-region scenarios (Table S24). The cost-based view of the decision (Reviewer 1, comment 16; our response to point 5 "
    "below) complements this.",
    "Section 4.6, Section 4.10, Conclusions, Supplementary Table S24 (new)."),
3: ("We now motivate each choice in Section 2.3 and tested the alternatives (new Table S17). The Poisson quasi-likelihood is used only "
    "as an estimating equation for the mean of |r|: under a log link it is consistent whenever the mean function is correctly specified, "
    "whatever the distribution of the absolute residuals (Gourieroux, Monfort & Trognon 1984), and, unlike least squares on log|r| "
    "(a log-normal model), it is not dominated by residuals close to zero. The constant in log(1 + T²) keeps the feature finite for "
    "spectra at the centre of the score space, and dividing Q by Q̃ only shifts the intercept"
    + (" (confirmed: identical intervals without it)" if qn_same else "") +
    ". Gamma and Gaussian log-link GLMs, the log-normal model, log T², un-normalised Q, a T² × Q interaction and a group-weighted fit "
    f"changed the coverage of GC-D by at most {dcov:.3f} and its interval score by {pm(100*min(dis))} to {pm(100*max(dis))} % across the "
    "new-season, next-season, new-instrument and soil-region scenarios; the interaction lowered the interval score slightly for new "
    "seasons and new instruments (by up to 1.5 %) but not for the next season or soil regions. We also note in Section 2.3 that σ only ranks spectra by expected difficulty, while q̂ is calibrated on "
    "the out-of-group scores whatever its form.",
    "Section 2.3, Section 4.5, Supplementary Table S17 (new), reference added."),
4: ("We agree and made the comparison more symmetric. (i) WCP-clip is now included in Tables 2 and 3 (five seeds; coverage "
    f"{f3(wcv.loc['mango_season_forward','coverage'])}–{f3(wcv.loc['mango_season_loso','coverage'])} on the mango season and instrument "
    "shifts, unbounded intervals remaining in the corn scenarios). (ii) We analysed whether the unboundedness is an artefact of the "
    "logistic estimator (new Table S20; details in our response to Reviewer 1, comment 4): an estimator that captures the shift "
    f"(AUC up to {w0.clf_auc.max():.2f}) produces extreme weights (effective sample size {pct(w0.ess_frac.min(),1)}–"
    f"{pct(w0.ess_frac.max())}), whereas an estimator that avoids them (three PLS scores) no longer corrects for the shift (coverage "
    f"{f3(w3.coverage.min())}–{f3(w3.coverage.max())}); caps of 5–100 gave {f3(wcap.coverage.min())}–{f3(wcap.coverage.max())} on the "
    "mango shifts. We "
    "therefore regard it as intrinsic to covariate-shift weighting when calibration and deployment spectra barely overlap. (iii) We "
    "argue explicitly why unbounded intervals are unacceptable in the NIR decision context: an interval that is unbounded for a share of "
    "samples cannot support a specification-limit decision. (iv) For HJ+ and HCP-D we state that they are unbounded for small K and "
    "therefore not alternatives where GC-D is most needed; they are compared with GC-D where they are finite (new instruments, soil "
    "regions; Section 4.4).",
    "Section 3.3, Section 4.1, Tables 2–3, Section 4.4, Supplementary Table S20 (new)."),
5: ("We extended the analysis as suggested (new Fig. 8, Tables S25a,b): a grid of limits from 12 to 19 % DM for mango and from 1 to "
    "8 % OC for soil, all relevant methods including ASTM-G, CQR and the oracle, and the point-prediction rule. For mango, GC-D had a "
    "false-acceptance rate no higher than SCP at every limit; for soil the differences between GC-D, SCP and the classical intervals were "
    f"small (L = 2 % OC: {f3(ds.loc[('GC-D',2.0),'false_acceptance'])} vs {f3(ds.loc[('SCP',2.0),'false_acceptance'])}), and CQR, whose "
    f"intervals are asymmetric, had the fewest false acceptances ({f3(ds.loc[('CQR',2.0),'false_acceptance'])}) at a lower yield — "
    "consistent with the level-dependent heteroscedasticity the reviewer points out. We tempered the claim as suggested: the oracle, "
    f"too, accepted only {f3(dm.loc[('ORACLE',16.0),'yield_compliant'])} of the compliant fruit at L = 16 % (GC-D "
    f"{f3(dm.loc[('GC-D',16.0),'yield_compliant'])}), so most of the yield loss relative to the point-prediction rule "
    f"({f3(dm.loc[('GC-D',16.0),'point_rule_yield'])}, but with {f3(dm.loc[('GC-D',16.0),'point_rule_false_acceptance'])} of the accepted "
    "fruit non-compliant) is the cost of any honest uncertainty statement. We discuss the practical and economic implications through "
    f"the break-even cost ratio: GC-D has the lower expected cost than SCP when a false acceptance costs more than {beS.loc[16.0]:.1f} "
    "times a false rejection at L = 16 %, with examples of contexts in which this holds and in which it does not.",
    "Section 4.8 (last paragraph), Fig. 8 (revised), Supplementary Table S25 (new)."),
}

OTHER = [
    "The Declaration of generative AI and AI-assisted technologies, which was omitted from the submitted file, has been restored "
    "in the form required by Elsevier.",
    "The CRediT statement, which still contained placeholders in the submitted file, has been completed.",
    "A statement on analyses added during the revision (Section 3.5) identifies everything that was done after the results were known; "
    "the details are in Supplementary Sections S16–S28. None of the analyses changed the methods or settings of the main study.",
    "Two references were added (Rubin 1981, Bayesian bootstrap; Gourieroux, Monfort & Trognon 1984, quasi-likelihood); both DOIs "
    "were checked against Crossref.",
    "Table 1 now prints single values instead of degenerate ranges; abbreviated column labels avoid broken table headers; typographic "
    "minus signs are used throughout.",
    "The code repository contains every new experiment and analysis (experiments/run_revision.py, run_simulation.py, "
    "revision_analyses.py), integrated into run_all.py, so that every number of the revision is regenerated from the public data.",
]

# ------------------------------------------------------------------------------------------------ document
d = Document()
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
for sec in d.sections:
    sec.left_margin = sec.right_margin = Cm(2.3); sec.top_margin = sec.bottom_margin = Cm(2.2)
md = []
def P(text, bold=False, italic=False, size=None, color=None, align=None, space=6):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = RGBColor(*color)
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(space)
    return p
def MD(t): md.append(t)

P("Response to the reviewers", bold=True, size=14); MD("# Response to the reviewers\n")
P("Manuscript TAL-D-26-07648 — “Group-conformal calibration of near-infrared prediction intervals for new seasons, instruments "
  "and regions using PLS diagnostics”", italic=True)
P("Dear Professor Pohl,")
intro = ("We thank you and the reviewers for the careful and constructive assessment of our manuscript. We have addressed every point; "
         "most comments led to new analyses, all of which are reported in the revised manuscript and, in detail, in the new "
         "Supplementary Sections S16–S28. Below, each comment is quoted in italics, followed by our response and the place of the change. "
         "Section, figure and table numbers refer to the revised manuscript; changes are highlighted in yellow in the file "
         "'Revised_Manuscript_highlighted'. Moved or deleted text is not highlighted and is listed here.")
P(intro); MD(f"Dear Professor Pohl,\n\n{intro}\n")
P("Main changes", bold=True); MD("## Main changes\n")
main = [
    "Positioning relative to hierarchical conformal prediction and to normalised conformal prediction moved to and expanded in the Introduction (R1.1–R1.3).",
    "New analyses: where diagnostic scaling is indispensable (conditional coverage; R1.5), unequal group sizes (R1.8), scale-model form (R1.9, R4.3), "
    "population effects (R1.11), estimation-based statistics (R1.14), uninformative intervals and a Q-based rejection rule (R1.15, R1.18, R4.2), "
    "decisions over a grid of limits for two analytes with a cost analysis (R1.16, R4.5), bias correction with labelled samples of the new group "
    "(R1.13, R1.17), WCP density-ratio variants and caps (R1.4, R4.4), and a synthetic study of single-deployment coverage (R1.19, R4.1).",
    "A new Section 4.10 'Practical recommendations'; Limitations and Conclusions revised.",
    "Shorter presentation of existing material: Table 4 and sensitivity/computational details moved to the Supplementary Material, former Section 4.9 merged into the Introduction (R1.23).",
    "Figures 4, 5, 6c, 7 and 8 revised; WCP-clip added to Tables 2–3.",
]
for m in main:
    d.add_paragraph(m, style="List Bullet"); MD(f"- {m}")
MD("")
for rid, name, RESP in [("R1", "Reviewer 1", R1), ("R4", "Reviewer 4", R4)]:
    P(name, bold=True, size=13, space=4); MD(f"## {name}\n")
    P(CM[rid]["summary"], italic=True, color=(0x40, 0x40, 0x40)); MD(f"*{CM[rid]['summary']}*\n")
    gen = ("We thank the reviewer for the positive assessment of the scale, design and honesty of the study and for the detailed "
           "suggestions, which we have followed throughout." if rid == "R1" else
           "We thank the reviewer for the positive assessment and for the substantive suggestions, which led to several new analyses.")
    P(gen); MD(gen + "\n")
    for c in CM[rid]["comments"]:
        n = c["n"]
        resp, where = RESP[n]
        P(f"Comment {rid}.{n}", bold=True, space=2); MD(f"### Comment {rid}.{n}\n")
        P(c["text"], italic=True, color=(0x40, 0x40, 0x40), space=4); MD(f"*{c['text']}*\n")
        p = d.add_paragraph(); r = p.add_run("Response. "); r.bold = True; p.add_run(resp); p.paragraph_format.space_after = Pt(4)
        MD(f"**Response.** {resp}\n")
        p = d.add_paragraph(); r = p.add_run("Changes in the manuscript: "); r.bold = True; r2 = p.add_run(where); r2.italic = True
        p.paragraph_format.space_after = Pt(10)
        MD(f"**Changes in the manuscript:** *{where}*\n")
P("Other changes", bold=True, size=13); MD("## Other changes\n")
for o in OTHER:
    d.add_paragraph(o, style="List Bullet"); MD(f"- {o}")
MD("")
P("We hope that the revised manuscript is now suitable for publication in Talanta.")
P("Yours sincerely,"); P("Divya Meena S (corresponding author), on behalf of all authors")
MD("We hope that the revised manuscript is now suitable for publication in Talanta.\n\nYours sincerely,\n\nDivya Meena S (corresponding author), on behalf of all authors\n")
d.save(os.path.join(HERE, "Response_to_Reviewers.docx"))
open(os.path.join(HERE, "response_to_reviewers.md"), "w").write("\n".join(md))
print("written Response_to_Reviewers.docx and response_to_reviewers.md;", len(R1), "+", len(R4), "responses")
