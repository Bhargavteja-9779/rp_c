# Response to the reviewers

Dear Professor Pohl,

We thank you and the reviewers for the careful and constructive assessment of our manuscript. We have addressed every point; most comments led to new analyses, all of which are reported in the revised manuscript and, in detail, in the new Supplementary Sections S16–S28. Below, each comment is quoted in italics, followed by our response and the place of the change. Section, figure and table numbers refer to the revised manuscript; changes are highlighted in yellow in the file 'Revised_Manuscript_highlighted'. Moved or deleted text is not highlighted and is listed here.

## Main changes

- Positioning relative to hierarchical conformal prediction and to normalised conformal prediction moved to and expanded in the Introduction (R1.1–R1.3).
- New analyses: where diagnostic scaling is indispensable (conditional coverage; R1.5), unequal group sizes (R1.8), scale-model form (R1.9, R4.3), population effects (R1.11), estimation-based statistics (R1.14), uninformative intervals and a Q-based rejection rule (R1.15, R1.18, R4.2), decisions over a grid of limits for two analytes with a cost analysis (R1.16, R4.5), bias correction with labelled samples of the new group (R1.13, R1.17), WCP density-ratio variants and caps (R1.4, R4.4), and a synthetic study of single-deployment coverage (R1.19, R4.1).
- A new Section 4.10 'Practical recommendations'; Limitations and Conclusions revised.
- Shorter presentation of existing material: Table 4 and sensitivity/computational details moved to the Supplementary Material, former Section 4.9 merged into the Introduction (R1.23).
- Figures 4, 5, 6c, 7 and 8 revised; WCP-clip added to Tables 2–3.

## Reviewer 1

*This manuscript addresses a timely and practically important problem in NIR multivariate calibration: prediction intervals calibrated under random or exchangeable sampling substantially under-cover when deployed on new seasons, instruments, populations or regions. The proposed GC-D method combines out-of-group conformity scores, group-balanced weights, and PLS T²/Q diagnostic scaling. The study is strong in scale and design, using 146,873 public spectra, 12 deployment-shift scenarios, unit-level leakage control, pre-registered hypotheses, factorial ablation and extensive supplementary analyses. However, the novelty is mainly combinatorial and applied rather than fundamental: group-conformal prediction and T²/Q diagnostics are established components, and the manuscript itself shows that a simple classical interval based on group-wise RMSECV captures much of the coverage benefit, while diagnostic scaling adds limited and often non-significant gains. No new chemical materials, sample preparation procedures or target analytes are introduced; the analytes are conventional and the data are public. The manuscript is commendably honest about failures (corn, KSSL→LUCAS transfer, tablets and small-group settings) and about the need for approximately ten or more groups for formal guarantees. Nevertheless, the practical positioning of GC-D relative to simpler alternatives, the incremental value of diagnostic scaling, and guidance for limited-group deployments require clearer articulation and stronger statistical support. I therefore recommend Major Revision, after which the work could become a useful contribution to Talanta.*

We thank the reviewer for the positive assessment of the scale, design and honesty of the study and for the detailed suggestions, which we have followed throughout.

### Comment R1.1

*The introduction correctly notes that group-level conformal prediction theory (Dunn et al., 2023; Lee et al., 2026) exists but has not been examined for NIR multivariate calibration. The authors should more clearly articulate: what is the essential distinction between this work and those statistical contributions? Is it the problem setting (NIRspecific group structures vs. general hierarchical data), or the technical adaptation challenges (PLS models vs. generic regression models)?*

**Response.** We agree that this needed to be stated explicitly. The coverage theory (Dunn et al.; Lee et al.) is borrowed and is not our contribution. The distinction is the adaptation to multivariate calibration, where three features of NIR practice are not covered by generic hierarchical data: (i) groups and physical samples are crossed (the same fruit or corn sample is scanned on several instruments), so the calibration must be unit-disjoint as well as group-disjoint, which generic leave-one-group-out schemes do not ensure; (ii) the PLS model's own diagnostics T² and Q describe the position of a new spectrum relative to the calibration space and can drive the interval width without a separate difficulty model; (iii) out-of-group residuals are a by-product of the group-wise cross-validation already used to select the number of latent variables, while the number of groups is typically small — exactly where the finite-sample guarantees of the hierarchical methods break down. The answer is therefore both: the problem setting (NIR group structures with crossed units and few groups) and the technical adaptation (PLS diagnostics, unit-disjoint cross-fitting, re-use of the group-wise cross-validation), together with the empirical evidence of how large the coverage loss of current practice is.

**Changes in the manuscript:** *New paragraph in the Introduction ('What distinguishes this work …'); contribution list revised.*

### Comment R1.2

*Section 4.9 provides an excellent statement of what is borrowed and what is new, but it appears at the end of the Discussion. Consider moving part of this content to the Introduction so readers understand the positioning before reading the method.*

**Response.** Thank you; we moved the statement of what is borrowed and what is new to the Introduction, immediately after the paragraph on the distinction (comment 1), and removed the former Section 4.9, whose remaining content (complementarity with calibration transfer) is now part of Sections 4.6 and 5.

**Changes in the manuscript:** *Introduction, paragraph 'We state at the outset what is borrowed …'; former Section 4.9 removed (sections renumbered).*

### Comment R1.3

*When discussing conformal prediction in chemometrics, provide a more detailed discussion of existing work on normalized conformal prediction in spectroscopy. Specifically: what are the similarities and differences between the normalized nonconformity score of Papadopoulos et al. (2011) and the σ(x) scaling used here?*

**Response.** Papadopoulos et al. (2011) normalise the residual by a non-parametric difficulty estimate, the average error (or distance) of the k nearest training points, fitted on a proper training set and calibrated on a random split; the same idea underlies the normalised inductive conformal predictor used for mid-infrared food adulteration (Jović et al.). Our σ(x) differs in two respects: it is a three-parameter parametric function of T² and Q, which extrapolates to spectra unlike any training spectrum (where nearest neighbours carry no information about the new region of the space), and it is fitted to out-of-group residuals, so it learns how the error grows when a spectrum comes from a group the model has not seen. A k-nearest-neighbour normalised predictor (NCP-kNN) was already included as a baseline; it under-covered the mango shift scenarios like SCP (new instruments 0.746 at nominal 0.90; Supplementary Tables S3, S4 and S14).

**Changes in the manuscript:** *Introduction, paragraph 'We state at the outset what is borrowed …'.*

### Comment R1.4

*The manuscript includes WCP as a comparator, but WCP returned unbounded intervals in several scenarios (coverage 1.000 with infinite interval score). The Methods should elaborate on the root cause of WCP's failure (density ratio concentrating more than α weight on test points when calibration and test groups are well-separated), and the Discussion should clarify whether this reflects a methodological limitation or an implementation limitation of the density ratio estimator.*

**Response.** We added the explanation to the Methods and an analysis of its cause to the Results. WCP places the weight w(x)/(Σwᵢ + w(x)) of the test spectrum at +∞, so the interval is unbounded whenever this share exceeds α. With seed 0, a logistic classifier separated calibration and deployment spectra with AUC 0.82–0.99; the effective sample size of the calibration weights fell to 0.2 %–9 % of the calibration set; and for new instruments 20 % of the deployment spectra carried more than α of the total weight. To separate a methodological from an estimator limitation, we repeated WCP with two other density-ratio estimators and with caps of 5–100 on the normalised ratios (new Table S20). A strongly regularised classifier (C = 0.01) still left up to 7 % of the intervals unbounded. A classifier restricted to three PLS scores produced bounded intervals but no longer separated the groups (AUC 0.70–0.77), so it hardly reweighted and covered only 0.766–0.817 on the mango shifts, like SCP. Caps of 5–100 gave coverage of 0.827–0.872 on the mango shifts (and 0.913–0.926 on the milder soil-region shift). Our reading is that the failure is intrinsic to covariate-shift weighting when calibration and deployment spectra barely overlap: an estimator that captures the shift produces extreme weights, and one that avoids extreme weights does not correct for the shift. With the ~30 calibration spectra of the corn scenarios, even a capped weight exceeds α of the total (a small-sample limitation).

**Changes in the manuscript:** *Section 3.3 (mechanism), Section 4.1 (analysis), Supplementary Table S20 (new).*

### Comment R1.5

*Among the three components of GC-D, out-of-group calibration was shown to be the dominant contributor to coverage improvement (Section 4.3, 0.795→0.861), while diagnostic scaling showed limited and mostly non-significant incremental benefit. The authors should more candidly discuss: if out-of-group calibration alone can be achieved via the simpler ASTM-G approach (group-wise RMSECV), in which specific scenarios is the diagnostic scaling component irreplaceable? The argument that "diagnostic scaling protects coverage under spectral drift" (Section 4.5) is compelling but requires systematic quantification: in which scenarios does out-of-group calibration without diagnostic scaling (G-W-A) fail while GC-D succeeds?*

**Response.** We agree and now address this directly. Out-of-group calibration without scaling (G-W-A), and therefore ASTM-G, achieves near-nominal coverage averaged over all spectra, but it gives every spectrum of a group the same width (ASTM-G varies the width only through the leverage). It thus over-covers typical spectra and under-covers atypical ones. Systematically across scenarios (new Fig. 7b, Table S21), G-W-A covered 0.953–0.982 of the spectra in the lowest Q/Q̃ decile, but only 0.614–0.819 in the highest decile of the new-season, next-season, new-instrument and soil-region scenarios, and ASTM-G covered 0.626–0.827; GC-D covered 0.837–0.923. In the KSSL → LUCAS transfer the highest decile was covered 0.090 by G-W-A and 0.772 by GC-D, and under a 2-nm wavelength shift G-W-A fell to 0.846 while GC-D covered 0.938 (Fig. 6c). The scaling is therefore irreplaceable whenever decisions are taken on individual samples, some of which are atypical — the typical situation after a change of season, instrument or region — whereas ASTM-G suffices if only the average coverage matters. We say this explicitly in Sections 4.3, 4.8 and 4.10 and in the Conclusions.

**Changes in the manuscript:** *Section 4.3 (last sentences), Section 4.8 (first paragraph), Fig. 7a,b, Supplementary Table S21 (new), Section 4.10, Conclusions.*

### Comment R1.6

*The post-hoc variants in Section 4.10 (GC-D2 and GC-CQR) show intriguing results: GC-CQR achieved the best interval score on new soil regions (7.77 vs. 11.90 for GC-D). The authors acknowledge these variants were designed after seeing the soil results and require independent confirmation. Consider more prominently emphasizing in the Conclusions that the "out-of-group calibration principle" transfers to other conformity scores (e.g., CQR)—this may be a more generalizable contribution than GC-D itself.*

**Response.** We agree and have strengthened this in the Conclusions: calibration on out-of-group errors, whatever the conformity score, is now presented as the main transferable message, with the T²/Q-scaled version as a cheap default for PLS models. Because GC-CQR was designed after seeing the soil results and evaluated on the same data, we keep it labelled as post-hoc and requiring independent confirmation, and we report its weaknesses (less sharp than GC-D on new mango instruments; lower coverage than CQR on corn).

**Changes in the manuscript:** *Conclusions, first paragraph; Section 4.9 (post-hoc) condensed.*

### Comment R1.7

*The rationale for the grouping strategy requires further justification. In the M-instr. scenario, 24 instruments are used as groups, but is there repeated measurement of the same physical samples across instruments? Section 3.2 mentions "7100 mango fruit were scanned on more than one instrument," with leakage control via physical unit exclusion. Consider adding a supplementary table specifying, for each scenario: number of groups, number of physical units per group, and number of physical units shared across groups (if any).*

**Response.** Yes: repeated measurement of the same physical samples across groups occurs only where groups are instruments. In the instrument scenario, 6,992 of the 10,508 fruit measured on the 24 held-out instruments were measured on more than one of them, and every corn and tablet sample was measured on every instrument; seasons, populations and soil regions share no units. The new Supplementary Table S16 lists, for every scenario, the number of held-out groups, spectra, physical units, units per group (median, minimum, maximum), units occurring in more than one group, and the range of calibration groups per outer fold. Every unit shared with a held-out group is removed from the training data of every model that predicts any of its spectra (asserted in the code for every outer and inner split).

**Changes in the manuscript:** *Section 3.2 (new paragraph), Supplementary Table S16 (new).*

### Comment R1.8

*The group-balanced weights (w_i = 1/(K·N_g)) should matter more when group sizes are unequal, but the experimental data show limited impact in scenarios with relatively uniform group sizes (mango seasons, instruments; 0.861→0.878). Consider designing a synthetic or semi-synthetic experiment with highly unbalanced group sizes to more fully test the practical utility of group-balanced weights.*

**Response.** We performed the suggested semi-synthetic experiment. In every outer fold of the new-instrument, new-season and soil-region scenarios, the training groups were subsampled to Zipf-like sizes (relative sizes 1, 2^−1.5, 3^−1.5, … in random order; three repetitions), so that the largest group held 42 %–59 % of the training spectra and the largest-to-smallest ratio was up to 375. Group-balanced weights then raised the coverage of the diagnostic-scaled interval from 0.843 to 0.866 (new instruments), from 0.854 to 0.876 (new seasons) and from 0.888 to 0.897 (soil regions), and similarly for absolute scores; with uniform weights the calibration reflects mainly the error of the largest group. The experiment also revealed a weakness that we now report as a limitation: with only ~3,000 training spectra, a few extrapolating organic-rich soil samples received extremely wide back-transformed intervals for every method, most for the diagnostic-scaled ones, which inflated the mean (not the median) interval score (Table S18).

**Changes in the manuscript:** *Section 4.3, Supplementary Table S18 (new), Section 4.11 (limitation added).*

### Comment R1.9

*The Poisson quasi-likelihood GLM for the σ(x) scaling model is statistically reasonable (robust to skewed absolute residuals), but the manuscript does not state whether other link functions (e.g., log-link Gaussian or Gamma) were tested for sensitivity. Consider adding a sensitivity analysis on the choice of link function to the Supplementary Material.*

**Response.** We added this sensitivity analysis (new Table S17): Gamma and Gaussian log-link GLMs, least squares on log|r| (log-normal), log T² instead of log(1 + T²), Q not normalised by Q̃, a T² × Q interaction term, a fit weighted by the group-balanced weights, and either diagnostic alone, for the new-season, next-season, new-instrument and soil-region scenarios. The alternatives changed the group-averaged coverage of GC-D by at most 0.006 and its interval score by −1.5 to +2.0 %. The choice of the Poisson quasi-likelihood is now motivated in Section 2.3 (consistent estimation of the mean of |r| under a log link whatever the distribution of the residuals; Gourieroux, Monfort & Trognon 1984).

**Changes in the manuscript:** *Section 2.3 (justification), Section 4.5, Supplementary Table S17 (new), reference added.*

### Comment R1.10

*Pre-registered hypothesis H3 states that "diagnostic normalisation lowers the interval score relative to absolute scores," but the results provide only partial support (5/9 scenarios, 1 significant). The Methods should more precisely define the testing conditions for H3: is directional consistency across all scenarios sufficient, or is statistical significance in the majority of scenarios required?*

**Response.** Thank you for pointing this out. The protocol stated H3 as a direction without a decision rule (unlike H1 and H2, which have explicit thresholds). We now state the rule that we apply, and say openly that it was formulated during the revision, after the results were known: H3 is supported when GC-D has the lower interval score in most main scenarios with Holm-significant differences in most, partly supported when only the first condition holds, and not supported otherwise. With 5 of 9 scenarios lower and 1 significant, H3 is partly supported, as reported in the submitted version. We also explain that the average interval score is not where the scaling matters (see comment 5).

**Changes in the manuscript:** *Section 3.4; Section 4.3.*

### Comment R1.11

*In the "new population" (M-pop.) scenario, GC-D outperformed SCP but not significantly (0.899 vs. 0.889). Section 4.1 suggests this may be because population effects are "absorbed" by season and instrument effects already represented in training. This explanation lacks direct empirical support. Consider adding an analysis: in the training data, are population effects indeed subsumed by season/instrument effects in the PLS latent variable space?*

**Response.** We agree that the explanation lacked direct support, and on testing it we found it only partly correct, so we replaced it. Direct evidence that a new population brings little extra error: its RMSEP was only 4 % above the random unit-wise cross-validation error of the same data, against 17 % for a new season and 24 % for a new instrument (new Table S27a). In the PLS latent space, however, populations are not simply relabelled seasons and instruments: season and instrument composition explained 40 % of the between-population variance of the population-mean scores (season alone 9 %), and season explained 14 % of the variance of the population-mean residuals (Table S27b). The revised text therefore says that the model generalises across lots, rather than that population effects are absorbed by season and instrument effects.

**Changes in the manuscript:** *Section 4.1 (third paragraph), Supplementary Table S27 (new).*

### Comment R1.12

*Regarding computational cost, Table S9 shows GC-D's method_s of 0.120 s, far below GPR (15.613 s) and BAG (14.980 s), but above ASTM-G (0.002 s). The Discussion should more clearly note that GC-D's computational cost primarily arises from the multiple PLS fits in group-wise cross-validation—which are typically already performed in chemometric practice (for selecting A). Thus, GC-D's "additional" computational cost is effectively near zero.*

**Response.** Agreed. Section 4.7 now states that almost all of the computation of GC-D is the group-wise cross-validation (K + 1 PLS fits) that chemometric practice performs anyway to choose the number of latent variables, so that the additional cost of GC-D (0.12 s and 83 MiB per held-out season) is effectively zero; the section was shortened at the same time (comment 23).

**Changes in the manuscript:** *Section 4.7.*

### Comment R1.13

*Figure 4 (scatter plot of coverage per held-out group) shows that for the new population scenario, coverage clusters around 0.88–0.92 for most methods, but there is a distinct low-coverage group (near 0). Section 4.6 mentions "population 114500" as the worst group but does not explain its peculiarity (2020 Kensington Pride fruit with mean DM far below the dataset average). Consider annotating this outlier group in Figure 4 and discussing in more detail: under such circumstances, even GC-D fails to achieve coverage—what supplementary measures are needed (e.g., a small number of labelled samples from the new group)?*

**Response.** We annotated population 114500 in Fig. 4 and extended the discussion in Section 4.8. Its fruit were green 'Kensington Pride' of 2020, harvested before maturity, with a mean DM far below that of the other lots, which the model over-predicted by 3.3 % DM; no calibration of interval width can repair such a bias. Following the suggestion, we tested labelled samples of the new group (comment 17): with a single labelled fruit, the bias-corrected and recalibrated interval (GC-D-BC) covered 0.938 of this population's spectra, against 0.012 without correction. We now recommend a few reference samples of a new group whenever a large group-level bias is plausible (Section 4.10).

**Changes in the manuscript:** *Fig. 4 (annotation), Section 4.8, Fig. 7d, Section 4.10.*

### Comment R1.14

*In the paired comparisons in Table 4, GC-D has a lower interval score than SCP in 7 of 9 main scenarios, but only the soil new region scenario is significant after Holm correction. For scenarios with n=5 (M-forward) and n=7 (M-season), even large effect sizes cannot reach significance (minimum p-values of 0.0625 and 0.0156, respectively). The statistical section should explicitly acknowledge this limitation and discuss: in practical scenarios with few groups, how should GC-D's advantage over SCP be assessed? Could Bayesian methods or confidence intervals of effect sizes be considered as supplementary evidence?*

**Response.** We now acknowledge the limitation explicitly in Section 3.4 and complement the tests by estimation (new Table S19): mean differences in interval score with 95 % bootstrap confidence intervals over the units of analysis, and posterior probabilities that GC-D has the lower mean interval score under the Bayesian bootstrap (Rubin 1981). Relative to SCP, GC-D lowered the mean interval score by 1–9 % in the mango and soil scenarios; the bootstrap interval excluded zero for new instruments, new populations and new soil regions; and the posterior probability was 0.96–1.00 (corn 0.26–1.00, i.e. no consistent advantage). We recommend judging a calibration method with few groups by such estimates together with the coverage it attains, rather than by a test on five to seven groups (Section 4.2).

**Changes in the manuscript:** *Section 3.4, Section 4.2, Supplementary Table S19 (new), reference added.*

### Comment R1.15

*The discussion of the corn dataset in Section 4.6 is commendably honest: with only two training instruments, no method reaches nominal coverage. However, the manuscript does not address a critical practical question: in real applications where a corn model is calibrated on only one instrument, what should the analyst do? Should they report "no valid prediction interval available" rather than a severely under-covering interval? Consider adding practical recommendations for such extreme scenarios to the Conclusions.*

**Response.** We added concrete recommendations. With a model calibrated on a single instrument or season, no interval method can anticipate the error of a new one, and reporting a severely under-covering interval is misleading. We therefore propose two checks computed from the calibration data alone, after which the analyst should report 'no reliable interval — model not valid for this sample': (i) the interval is at least as wide as the central 90 % range of the training reference values, or (ii) Q/Q̃ exceeds the 99 % quantile of the out-of-group calibration values. At least one check fired for 38 %–65 % of the corn test spectra and 50 % of the KSSL → LUCAS spectra, against 2.0 %–5.6 % in the mango and soil-region scenarios; for the tablets, which were calibrated on one instrument, the Q check flagged 100 % of the second-instrument spectra and 0.2 % of the calibration-instrument spectra. When a check fires for a large share of a new instrument's spectra, the model should be transferred or recalibrated with a few reference samples (bias correction, comment 17).

**Changes in the manuscript:** *Section 4.6 (new paragraph), Section 4.10, Conclusions, Supplementary Table S24 (new).*

### Comment R1.16

*Section 4.6 discusses the consequences for specification-limit decisions (Table S11, Figure 8), showing that GC-D's false acceptance rate at L=16 is 0.021 vs. SCP's 0.041, but "yield of compliant fruit" drops from 0.434 to 0.342. This is an important trade-off, but the manuscript does not discuss how to choose this trade-off point in practical decision-making. Consider adding a discussion: in what decision contexts (e.g., highvalue crops, safety-critical applications) is a lower false acceptance rate worth sacrificing compliant yield?*

**Response.** We extended the decision analysis in Section 4.8 to a grid of limits (12–19 % DM) and to soil organic carbon (1–8 % OC), and we added a cost analysis (new Fig. 8, Tables S25a,b). With c the cost of accepting a non-compliant item relative to rejecting a compliant one, GC-D has a lower expected cost than SCP for c above 8.2 at L = 16 % DM (3.2–37.7 over the grid). We discuss the decision contexts: contractual penalties for out-of-specification lots, minimum-maturity rules or safety-related attributes (c ≫ 10) favour GC-D, whereas bulk processing in which a rejected fruit is merely downgraded (c ≈ 1) favours accepting on the point prediction. The point-prediction rule kept 0.831 of the compliant fruit at L = 16 %, but 0.145 of the accepted fruit were non-compliant.

**Changes in the manuscript:** *Section 4.8 (last paragraph), Fig. 8 (revised), Supplementary Table S25 (new).*

### Comment R1.17

*Section 4.7 on "worst-group" analysis shows that GC-D's worst coverage in the new instrument scenario is only 0.447 (Table S4a). This is a concern: even if GC-D's average coverage is near nominal, some instruments remain severely under-covered. The manuscript attributes this to instrument bias but does not discuss whether simple bias correction (using a few reference samples from the new instrument) could improve it. Consider adding an analysis: under the condition of 2–5 reference samples from the new instrument, how does GC-D's coverage change after bias correction?*

**Response.** A clarification first: the worst new-instrument coverage of GC-D in Table S4a is 0.356; 0.447 is the value of GC-D+ (the variant with the finite-sample correction). We performed the suggested analysis: k = 1, 2, 3, 5 and 10 labelled fruit of the new instrument (20 random draws per instrument), used (a) to shift the interval centre by their mean residual, and (b) in a recalibrated variant (GC-D-BC) that mimics the same correction in every calibration group before the scale model and q̂ are fitted, so that the calibration accounts for the noise of the bias estimate. Shifting with three fruit raised the worst-instrument coverage from 0.356 to 0.755, but with one fruit the noisy estimate lowered the group-averaged coverage to 0.847, and with more fruit the shifted intervals over-covered (0.936 at k = 10). GC-D-BC kept the average coverage at 0.877–0.886 for every k while narrowing the intervals (interval score 5.90 vs 6.21 at k = 3; worst instrument 0.729). For new seasons, whose biases are small relative to the fruit-to-fruit variation, a few fruit did not help (Section 4.8). Bias correction therefore pays for large group-level biases and should be calibrated as in GC-D-BC.

**Changes in the manuscript:** *Section 4.8 (second paragraph), Fig. 7c,d (new), Supplementary Table S22 (new), Section 4.10.*

### Comment R1.18

*The simulated drift experiments in Section 4.5 (Figure 6c) show that a 2 nm wavelength shift reduces SCP coverage to 0.755 while GC-D covers 0.938; 1% white noise reduces SCP to 0.398 and GC-D to 0.703. However, GC-D's coverage of 0.703 under white noise remains far below the nominal 0.90. The manuscript notes that such spectra should be "rejected" rather than reported with intervals, but does not discuss the implementation of a rejection rule. Consider adding: how to design a practical rejection rule based on the Q diagnostic? What are its false positive and false negative rates?*

**Response.** We designed and evaluated such a rule: withhold the interval when Q/Q̃ exceeds the 95 % or 99 % quantile of the out-of-group calibration values (computed from the training data alone), optionally also when T² exceeds its 99 % quantile. On the perturbed new-season spectra (new Table S23), the 99 % rule rejected 2.7 % of the unperturbed spectra (false positives; 6.9 % with the 95 % rule), 71 % of the spectra with 1 % noise and 100 % with 3 % noise. Its false negatives were perturbations that hardly change Q (0.3 % noise: 5 % rejected; gain and baseline tilt, which the derivative preprocessing removes; shifts of 0.5–1 nm), which GC-D covered at least 0.894 anyway. We also report its limit: the retained 1 %-noise spectra were covered only 0.741, and the stricter 95 % rule rejected 97 % of them at the price of more false rejections.

**Changes in the manuscript:** *Section 4.5, Supplementary Table S23 (new), Section 4.10.*

### Comment R1.19

*The Conclusions recommend that "calibration campaigns should span as many seasons or instruments as possible—about ten or more for formal group-level guarantees." However, the practical feasibility of this recommendation deserves discussion: in many NIR applications (e.g., a single harvest season crop, a singleinstrument laboratory), obtaining 10+ groups is unrealistic. Consider adding to the Discussion: under conditions of limited groups, is GC-D's "partial benefit" relative to SCP still worth adopting? How should its positioning of "benefit without guarantee" be communicated to practitioners?*

**Response.** This is an important practical point. We now (i) state in Section 2.4 and Section 4.4 that the threshold for formal guarantees is K ≥ 1/α − 1 and therefore depends on the nominal level (ten groups at 90 %, twenty at 95 %, five at 80 %); (ii) quantify, with real data and a new synthetic study (Fig. S3, Table S26), what GC-D delivers with few groups: on average it removes the systematic under-coverage of random calibration for every K from 3 to 50 (α = 0.10: 0.885–0.902 vs 0.846 for random calibration at K = 3), but the coverage of one deployment remains uncertain by several percentage points; (iii) recommend how to communicate this 'benefit without guarantee' (Section 4.10): report that coverage was verified empirically and may deviate for a single new group, using the group-to-group spread of the group-wise validation as the measure. For a single-season crop or a single-instrument laboratory, no interval method can anticipate the error of a new season or instrument; we recommend a few reference samples of the new group (comment 17) and the checks of comment 15.

**Changes in the manuscript:** *Sections 2.4, 4.4, 4.10, Conclusions; Supplementary Section S26 and Fig. S3 (new).*

### Comment R1.20

*The manuscript states that all code is in run_all.py, reproducing every number, table, and figure. For the final version, consider including a persistent identifier (e.g., Zenodo DOI) for the code repository in the Data Availability statement to enhance the credibility of reproducibility.*

**Response.** We will deposit the code, configuration and result files in Zenodo, and the Data availability statement says so. A DOI can be inserted when the archive is created; we will add it at the proof stage if it is not yet available at resubmission.

**Changes in the manuscript:** *Data availability.*

### Comment R1.21

*In Table S9 (computational cost), GC-D's peak_MiB is 83.338 MB while ORACLE is only 0.747 MB. This large difference deserves explanation: why is ORACLE's memory footprint so low? Is it because it does not require fitting multiple PLS models? Consider annotating the table to explain the sources of memory differences across methods.*

**Response.** ORACLE needs no additional model: it computes quantiles of residuals of the final model, which already exist, on the test group. GC-D needs about 83 MiB because it evaluates T² and Q of every training spectrum under its out-of-group fold model, which requires reconstructing the n × p training matrix in double precision (≈ 70 000 × 103 × 8 bytes ≈ 58 MB) plus the scale-model fit. We added a note to Table S9 that explains the memory of every method family (residual sorting only; out-of-fold diagnostics; an additional PLS fit; a second cross-validation; the GPR kernel matrix; 25 bagged models).

**Changes in the manuscript:** *Supplementary Table S9 (note added).*

### Comment R1.22

*Tables S3a and S3b provide coverage results at nominal levels 0.95 and 0.80, but the main text primarily discusses 0.90. Consider briefly mentioning in the main text: is GC- D's advantage over SCP consistent across different nominal levels? If consistent, this strengthens the robustness of the conclusions; if not, the reasons should be discussed.*

**Response.** The advantage is consistent across nominal levels. On the mango season and instrument scenarios GC-D covered 5–11 percentage points more than SCP at 0.80, 0.90 and 0.95, the difference has the same sign at all three levels in every mango and soil scenario, and the group-averaged coverage of GC-D deviated from the nominal level by at most 0.030. This is now stated in Section 4.2 and in the note to Table S3.

**Changes in the manuscript:** *Section 4.2 (end of second paragraph); Supplementary Table S3 (note).*

### Comment R1.23

*Regarding manuscript length and structure: The main text is approximately 20 pages (including figures and tables), which is on the long side for a Talanta Research Paper. Consider moving some content (e.g., detailed sensitivity analyses, per-scenario discussions) to the Supplementary Material in revision, keeping the main text focused on core arguments and primary results.*

**Response.** We moved Table 4 to the Supplementary Material (it is a subset of Table S14), the sensitivity details to Table S5/S17, the computational details to Table S9, and the former Section 4.9 to the Introduction, and we condensed Sections 4.5–4.7 and 4.9. The additional analyses requested by both reviewers (29 points) could not be added without some text, but we kept their details in the Supplementary Material (new Sections S16–S28). The main text now has 7,136 words of body text against 5,617 in the submitted version, three tables instead of four and the same eight figures.

**Changes in the manuscript:** *Throughout; Table 4 → Supplementary Table S14; Supplementary Sections S16–S28.*

### Comment R1.24

*Regarding figure readability: Figure 5 (factorial ablation) uses an intuitive color coding (red = under-coverage), but consider adding a "GC-D" column to clearly indicate the reference baseline. In Figure 6(c), the x-axis labels for test-time perturbations are too dense—consider simplifying or using clearer labels.*

**Response.** Fig. 5 now frames the GC-D column (= G-W-D) in both panels and labels it as the reference. In Fig. 6c the perturbation levels are shown as short horizontal tick labels grouped under the perturbation type (none, gain, tilt, λ shift, noise), and the panel was widened.

**Changes in the manuscript:** *Fig. 5, Fig. 6c.*

## Reviewer 4

*The manuscript addresses a genuinely important and under-examined problem in chemometrics—namely, that NIR prediction intervals calibrated under random exchangeability assumptions systematically under-cover when models are deployed on new seasons, instruments or regions—and the proposed group-conformal calibration with PLS diagnostics (GC-D) is conceptually sound, clearly presented and evaluated on a commendably large and diverse collection of public data (146,873 spectra across four data sets and twelve deployment-shift scenarios), with a pre-registered analysis protocol, honest reporting of negative and null results, and full reproducibility; nevertheless, several substantive issues require clarification or revision before the work can be considered for publication.*

We thank the reviewer for the positive assessment and for the substantive suggestions, which led to several new analyses.

### Comment R4.1

*although the authors are candid that GC-D's coverage is asymptotic in the number of groups and empirically verified rather than guaranteed, the manuscript would benefit from a more systematic characterisation of the finite-sample behaviour of the groupaveraged coverage estimator as a function of K, since the reported variability across heldout groups for the six-season mango case (Fig. 4) suggests that practitioners with few calibration groups may face substantial group-to-group dispersion even when the average coverage appears nominal; a simulation study or a more explicit variance decomposition (between-group versus within-group) would help users judge the reliability of a single deployment, and the recommendation of "about ten or more groups" should be qualified by the observation that this threshold is specific to α = 0.10 and to the group-size distribution of the present data.*

**Response.** We added both requested analyses. (i) Variance decomposition in the real data: the coverage of GC-D in individual held-out groups had a standard deviation of 0.06–0.15, of which 93 %–99 % was between-group variation and the remainder the sampling variation of a coverage proportion (new Table S28). (ii) A synthetic hierarchical study (Supplementary Section S26, Fig. S3, Table S26) of the coverage attained in a single new group for K = 3–50, α = 0.05, 0.10 and 0.20 and balanced or log-normally distributed group sizes: out-of-group calibration was close to nominal on average for every K, but the standard deviation of single-deployment coverage fell only from 0.11 (K = 3) to 0.07 (K = 50) at α = 0.10, because it is caused by the new group's own effect, which only information about that group can remove. As the reviewer anticipated, the 'about ten groups' threshold is specific to α = 0.10: the finite-sample correction became finite at K = 20 for α = 0.05, 10 for α = 0.10, 5 for α = 0.20, i.e. at K ≥ 1/α − 1, for balanced and unbalanced group sizes alike. The recommendation is qualified accordingly in Sections 2.4, 4.4, 4.10 and 5 and in the abstract.

**Changes in the manuscript:** *Sections 2.4 and 4.4 (new paragraph), 4.10, 4.11, Conclusions, Abstract; Supplementary Tables S26 and S28 and Fig. S3 (new).*

### Comment R4.2

*the corn results deserve more careful framing: with only two training instruments, no method reached nominal coverage, and the authors correctly attribute this to an uncorrected instrument shift that makes the PLS model weakly informative (RMSEP 0.61–2.45 times the reference SD), but the manuscript should state more explicitly that in such regimes interval calibration is fundamentally limited by the point predictor's validity, and that the apparent "failure" of GC-D is not a defect of the calibration principle but a signal that model transfer or bias correction must precede uncertainty quantification; the same applies to the KSSL→LUCAS stress test, where GC-D reached only 0.604 and HCP-D 0.712 with analytically useless widths, and the paper would be strengthened by a decision-theoretic discussion of when an interval should be reported as "uninformative" rather than merely wide.*

**Response.** We agree with this framing and adopted it. Section 4.6 now states that in the corn and KSSL → LUCAS settings the failure is that of the point predictor, not of the calibration principle: an interval can only quantify the error of a model that is still valid for the new group, and model transfer or bias correction must precede uncertainty quantification. We also added the decision-theoretic element: two checks computed from the calibration data (interval as wide as the range of the calibration reference values; Q/Q̃ above the 99 % calibration quantile) define when an interval should be reported as uninformative ('model not valid for this sample'). They fired for 38 %–65 % of the corn spectra and 50 % of the KSSL → LUCAS spectra, but for at most 5.6 % in the mango and soil-region scenarios (Table S24). The cost-based view of the decision (Reviewer 1, comment 16; our response to point 5 below) complements this.

**Changes in the manuscript:** *Section 4.6, Section 4.10, Conclusions, Supplementary Table S24 (new).*

### Comment R4.3

*the diagnostic scale model in Eq. (3), fitted by a log-link Poisson quasi-likelihood GLM on absolute residuals with log(1+T²) and log(Q/Q̂ ) as covariates and a floor at 10% of the median σ, is a reasonable engineering choice but is presented without sufficient justification or sensitivity analysis: the choice of the Poisson quasi-likelihood versus, for example, a gamma GLM or a log-normal model for |r| should be motivated, the additive constant in log(1+T²) and the median normalisation of Q should be shown to be innocuous (the Supplementary Table S5 sensitivity analysis varies the σ floor and the number of LVs but not the functional form of the scale model), and the interaction between T² and Q—which the additive log-linear model ignores—could matter for spectra that are simultaneously high-leverage and poorly reconstructed, a point the authors acknowledge only implicitly in the discussion of spectral drift.*

**Response.** We now motivate each choice in Section 2.3 and tested the alternatives (new Table S17). The Poisson quasi-likelihood is used only as an estimating equation for the mean of |r|: under a log link it is consistent whenever the mean function is correctly specified, whatever the distribution of the absolute residuals (Gourieroux, Monfort & Trognon 1984), and, unlike least squares on log|r| (a log-normal model), it is not dominated by residuals close to zero. The constant in log(1 + T²) keeps the feature finite for spectra at the centre of the score space, and dividing Q by Q̃ only shifts the intercept. Gamma and Gaussian log-link GLMs, the log-normal model, log T², un-normalised Q, a T² × Q interaction and a group-weighted fit changed the coverage of GC-D by at most 0.006 and its interval score by −1.5 to +2.0 % across the new-season, next-season, new-instrument and soil-region scenarios; the interaction lowered the interval score slightly for new seasons and new instruments (by up to 1.5 %) but not for the next season or soil regions. We also note in Section 2.3 that σ only ranks spectra by expected difficulty, while q̂ is calibrated on the out-of-group scores whatever its form.

**Changes in the manuscript:** *Section 2.3, Section 4.5, Supplementary Table S17 (new), reference added.*

### Comment R4.4

*the comparison with weighted conformal prediction (WCP) is somewhat asymmetric: WCP returns unbounded intervals in every scenario because the estimated density ratios place more than α of the weight on the test point, and the clipped variant (WCP-clip) achieves coverage 0.851–0.855 at the cost of 0–1% unbounded intervals, yet the manuscript does not report WCP-clip's interval scores in the main tables or discuss whether its unboundedness is an artefact of the logistic density-ratio estimator rather than an intrinsic property of covariate-shift conformal methods; a fairer comparison would either include WCP-clip in Table 3 or explicitly argue why unbounded intervals are unacceptable in the NIR decision context, and the same concern applies to the comparison with HJ+ and HCP-D, which are unbounded for small K and therefore not directly comparable to GC-D in the scenarios where GC-D is most needed.*

**Response.** We agree and made the comparison more symmetric. (i) WCP-clip is now included in Tables 2 and 3 (five seeds; coverage 0.822–0.855 on the mango season and instrument shifts, unbounded intervals remaining in the corn scenarios). (ii) We analysed whether the unboundedness is an artefact of the logistic estimator (new Table S20; details in our response to Reviewer 1, comment 4): an estimator that captures the shift (AUC up to 0.99) produces extreme weights (effective sample size 0.2 %–9 %), whereas an estimator that avoids them (three PLS scores) no longer corrects for the shift (coverage 0.766–0.817); caps of 5–100 gave 0.827–0.872 on the mango shifts. We therefore regard it as intrinsic to covariate-shift weighting when calibration and deployment spectra barely overlap. (iii) We argue explicitly why unbounded intervals are unacceptable in the NIR decision context: an interval that is unbounded for a share of samples cannot support a specification-limit decision. (iv) For HJ+ and HCP-D we state that they are unbounded for small K and therefore not alternatives where GC-D is most needed; they are compared with GC-D where they are finite (new instruments, soil regions; Section 4.4).

**Changes in the manuscript:** *Section 3.3, Section 4.1, Tables 2–3, Section 4.4, Supplementary Table S20 (new).*

### Comment R4.5

*the specification-limit decision analysis (Fig. 8) is a valuable addition but is limited to mango new-season data and two thresholds (L = 16 and 17% DM); the false-acceptance rates (0.021–0.024 for GC-D versus 0.039–0.057 for SCP and classical intervals) are encouraging, but the analysis would be considerably more convincing if extended to at least one other data set (e.g. soil organic carbon, where the level-dependent heteroscedasticity documented in Section 4.10 makes symmetric intervals questionable) and to a range of L values, and if the yield loss (0.342 versus 0.434 accepted compliant fruit at L = 16%) were discussed in terms of its practical and economic implications rather than merely reported; moreover, the claim that GC-D "reduced false acceptances in specification-limit decisions" should be tempered by the observation that the oracle itself accepted only 0.375 of compliant fruit, so that even a perfectly calibrated interval entails a substantial yield penalty relative to a point-prediction rule.*

**Response.** We extended the analysis as suggested (new Fig. 8, Tables S25a,b): a grid of limits from 12 to 19 % DM for mango and from 1 to 8 % OC for soil, all relevant methods including ASTM-G, CQR and the oracle, and the point-prediction rule. For mango, GC-D had a false-acceptance rate no higher than SCP at every limit; for soil the differences between GC-D, SCP and the classical intervals were small (L = 2 % OC: 0.030 vs 0.031), and CQR, whose intervals are asymmetric, had the fewest false acceptances (0.010) at a lower yield — consistent with the level-dependent heteroscedasticity the reviewer points out. We tempered the claim as suggested: the oracle, too, accepted only 0.375 of the compliant fruit at L = 16 % (GC-D 0.342), so most of the yield loss relative to the point-prediction rule (0.831, but with 0.145 of the accepted fruit non-compliant) is the cost of any honest uncertainty statement. We discuss the practical and economic implications through the break-even cost ratio: GC-D has the lower expected cost than SCP when a false acceptance costs more than 8.2 times a false rejection at L = 16 %, with examples of contexts in which this holds and in which it does not.

**Changes in the manuscript:** *Section 4.8 (last paragraph), Fig. 8 (revised), Supplementary Table S25 (new).*

## Other changes

- The Declaration of generative AI and AI-assisted technologies, which was omitted from the submitted file, has been restored in the form required by Elsevier.
- The CRediT statement, which still contained placeholders in the submitted file, has been completed.
- A statement on analyses added during the revision (Section 3.5) identifies everything that was done after the results were known; the details are in Supplementary Sections S16–S28. None of the analyses changed the methods or settings of the main study.
- Two references were added (Rubin 1981, Bayesian bootstrap; Gourieroux, Monfort & Trognon 1984, quasi-likelihood); both DOIs were checked against Crossref.
- Table 1 now prints single values instead of degenerate ranges; abbreviated column labels avoid broken table headers; typographic minus signs are used throughout.
- The code repository contains every new experiment and analysis (experiments/run_revision.py, run_simulation.py, revision_analyses.py), integrated into run_all.py, so that every number of the revision is regenerated from the public data.

We hope that the revised manuscript is now suitable for publication in Talanta.

Yours sincerely,

Divya Meena S (corresponding author), on behalf of all authors
