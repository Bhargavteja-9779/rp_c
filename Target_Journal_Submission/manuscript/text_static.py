"""Results-independent manuscript text (Introduction, Theory, Experimental).

Blocks are tuples consumed by build_manuscript.py:
  ("h1"|"h2"|"h3", text) · ("p", text) · ("eq", latex-like text, number) · ("bullets", [..])
Citations are inserted with C("key", ...) so that numbering follows first appearance.
"""


def introduction(C, N):
    return [
        ("h1", "1. Introduction"),
        ("p", "Near-infrared (NIR) spectroscopy combined with multivariate calibration is used routinely to predict "
              "composition in agriculture, food, soil and pharmaceutical analysis because it is rapid, non-destructive "
              f"and inexpensive per sample {C('walsh2020', 'wold2001')}. A predicted concentration is, however, only "
              "useful for a decision when it is accompanied by an honest statement of its uncertainty. Standard "
              "practice derives sample-specific prediction intervals from the calibration error and the leverage of the "
              f"new spectrum {C('astm1655', 'faber1997', 'denham1997')}, or from linearisation and resampling "
              f"approximations {C('fernandez2003', 'zhang2009', 'romera2010')}. These intervals rest on distributional "
              "assumptions and, more importantly, on the assumption that future samples resemble the calibration "
              "samples."),
        ("p", "Conformal prediction offers prediction intervals with a finite-sample, distribution-free coverage "
              f"guarantee under a single assumption: exchangeability of calibration and test data {C('vovk2005', 'lei2018', 'angelopoulos2023')}. "
              "It has begun to enter chemometrics and analytical chemistry: jackknife+ intervals for PLS regression "
              f"{C('lin2022')}, normalised inductive conformal predictors for mid-infrared food adulteration "
              f"{C('jovic2025')}, conformalised uncertainty models for soil organic carbon from Raman spectra "
              f"{C('wiens2026')}, aggregated inductive conformal prediction for NIR spectra {C('cui2026ssrn')} and "
              f"multiview conformal identification of microplastics {C('parham2026')}; it has also been used for "
              f"applicability-domain assessment in QSAR {C('norinder2014')}. In the regression studies, calibration "
              "and test samples are obtained by random partitioning of one data pool, which is exactly the setting in "
              "which the exchangeability assumption holds by construction."),
        ("p", "The setting in which NIR calibrations are actually used is different. A fruit-quality model is "
              "calibrated on past harvest seasons and applied to the next one; a model developed on one spectrometer "
              "is used on another unit; a soil model is applied to a region that did not contribute calibration "
              f"samples. Such season, instrument and region effects are a central problem of NIR practice "
              f"{C('feudale2002', 'workman2018', 'anderson2020', 'sun2020')} and motivate calibration transfer and "
              f"domain-adaptation methods {C('nikzad2018', 'mikulasek2023')}. Under these deployment shifts calibration "
              "and test samples are no longer exchangeable, so the coverage guarantee of randomly calibrated conformal "
              "intervals no longer applies. Statistical work has proposed weighted conformal prediction for covariate "
              f"shift {C('tibshirani2019', 'barber2023')}, adaptive procedures for sequential shift {C('gibbs2021')} and, "
              f"most relevant here, conformal methods for hierarchical (grouped) data {C('dunn2023', 'lee2026', 'mallick2026')}, "
              "which guarantee coverage for an observation from a new group when the groups themselves are "
              "exchangeable. To our knowledge these group-level ideas have not been examined for multivariate "
              "calibration, and it is not known how large the coverage loss of current practice is in real NIR "
              "deployments, nor whether the remedy is practical with the limited number of seasons or instruments "
              "typically available."),
        ("p", "This work addresses that gap with three contributions. (i) We quantify, on four public data sets "
              f"comprising {N['n_spectra_total']} spectra and {N['n_shift_tasks']} deployment-shift scenarios, how much "
              "classical PLS intervals, random-split conformal methods and model-based uncertainty estimates "
              "miscover when a calibration meets a new season, instrument, population or region. (ii) We propose a "
              "group-conformal calibration for PLS models (GC-D) that computes conformity scores out-of-group with "
              "group-balanced weights and scales them by the classical chemometric diagnostics Hotelling T² and Q "
              "residual, so that interval width grows for spectra that extrapolate. (iii) We test every component "
              "in a factorial ablation, examine when distribution-free group-level guarantees are attainable, and "
              "evaluate the consequences for specification-limit decisions. The experimental protocol, hypotheses "
              "and primary end-points were fixed before the held-out evaluation."),
    ]


def theory(C):
    return [
        ("h1", "2. Theory"),
        ("h2", "2.1. Problem setting"),
        ("p", "Let the calibration data consist of spectra xᵢ ∈ ℝᵖ with reference values yᵢ, i = 1, …, n, each "
              "belonging to one of K groups gᵢ ∈ {1, …, K} (harvest seasons, instruments, populations or regions) "
              "and to a physical unit uᵢ (fruit, soil sample, tablet). Several spectra may share a unit. A model is "
              "deployed on spectra of a new group K + 1. For a miscoverage level α we seek an interval C(x) with"),
        ("eq", "P{ Y_new ∈ C(X_new) } ≥ 1 − α,   (X_new, Y_new) drawn from the new group", "1"),
        ("p", "Random-split conformal prediction attains (1) when calibration and test points are exchangeable "
              f"{C('lei2018')}. Here we instead assume hierarchical exchangeability {C('lee2026')}: the groups are "
              "exchangeable with one another (a new season is a priori like past seasons) and spectra are "
              "exchangeable within a group, while spectra of the same group may share a common effect (for example a "
              "seasonal bias)."),
        ("h2", "2.2. PLS model and spectral diagnostics"),
        ("p", f"The point predictor is PLS1 regression {C('wold2001')} with A latent variables, ŷ(x) = ȳ + (x − x̄)ᵀ R_A q_A, "
              "where R_A = W_A (P_Aᵀ W_A)⁻¹ maps a mean-centred spectrum to its scores t = R_Aᵀ(x − x̄). Two "
              f"diagnostics describe how a spectrum relates to the calibration space {C('jackson1979')}:"),
        ("eq", "T²(x) = Σₐ tₐ² / sₐ²,     Q(x) = ‖(x − x̄) − P_A t‖²", "2"),
        ("p", "where sₐ² is the variance of the a-th training score. T² measures extrapolation within the model "
              "subspace and Q measures spectral variation the model has not seen. The leverage used in classical "
              "intervals is h(x) = 1/n + Σₐ tₐ²/(tₐᵀtₐ), a rescaled version of T²."),
        ("h2", "2.3. Group-conformal calibration with diagnostic scaling (GC-D)"),
        ("p", "Step 1 (out-of-group residuals). The calibration groups are partitioned into folds (one group per "
              "fold when K is small). For each fold k, a PLS model μ̂₋ₖ is fitted on the remaining groups after "
              "removing every unit that also occurs in fold k, so that no physical sample contributes to the model "
              "that predicts it. The out-of-group residual of spectrum i in fold k(i) is rᵢ = yᵢ − μ̂₋ₖ₍ᵢ₎(xᵢ), with "
              "diagnostics T²ᵢ and Qᵢ computed by the same model. The number of latent variables A is chosen by "
              "minimising the group-balanced root mean squared error of these residuals, so the step costs nothing "
              "beyond the group-wise cross-validation that is usual practice."),
        ("p", "Step 2 (diagnostic scale). The expected absolute residual is modelled as"),
        ("eq", "log σ(x) = β₀ + β₁ log(1 + T²(x)) + β₂ log(Q(x)/Q̃)", "3"),
        ("p", "with Q̃ the median training Q of the final model. β is estimated by a log-link generalised linear "
              "model with Poisson quasi-likelihood on (|rᵢ|, T²ᵢ, Qᵢ), which is robust to the skewness of absolute "
              "residuals; σ is bounded below by 10 % of its median to avoid division by near-zero scales. Eq. (3) "
              "generalises the √(1 + h) factor of classical intervals by letting the data decide how strongly "
              "extrapolation (T²) and unmodelled spectral variation (Q) inflate the error."),
        ("p", "Step 3 (group-balanced quantile). With conformity scores sᵢ = |rᵢ|/σ(xᵢ) and weights "
              "wᵢ = 1/(K·N_{gᵢ}), where N_g is the number of spectra in group g, every group contributes the same total "
              "mass regardless of its size. The calibrated multiplier is"),
        ("eq", "q̂ = inf{ t : Σᵢ wᵢ 1(sᵢ ≤ t) ≥ 1 − α }", "4"),
        ("p", "Step 4 (interval). The final PLS model, fitted on all calibration spectra, gives for a new spectrum"),
        ("eq", "C(x) = [ ŷ(x) − q̂ σ(x),  ŷ(x) + q̂ σ(x) ]", "5"),
        ("h2", "2.4. Coverage guarantees and their limits"),
        ("p", "Because q̂ in (4) equalises group contributions, it estimates the quantile of the score distribution "
              "of a randomly chosen new group (pooled empirical distribution functions), which is asymptotically "
              f"valid as K grows {C('dunn2023')}. Finite-sample guarantees under hierarchical exchangeability are "
              f"available for two variants that we also evaluate {C('lee2026')}: hierarchical split conformal "
              "prediction (HCP), in which half of the groups fit the model and σ and the other K₁ groups calibrate "
              "with weights 1/((K₁ + 1)N_g) and a point mass 1/(K₁ + 1) at +∞, has coverage ≥ 1 − α; the hierarchical "
              f"jackknife+ (HJ+), the leave-one-group-out analogue of the jackknife+ {C('barber2021')}, has coverage "
              "≥ 1 − 2α. The point mass at +∞ implies that a finite interval at level 1 − α requires K₁ + 1 > 1/α, "
              "i.e. at least 10 calibration groups at α = 0.10 for HCP. With six past harvest seasons a "
              "distribution-free season-level guarantee is therefore impossible at 90 % coverage; the cross-fitted "
              "GC-D trades this guarantee for usability, and its coverage must be assessed empirically, which is "
              "what Section 4 does."),
    ]


def experimental(C, N):
    return [
        ("h1", "3. Experimental"),
        ("h2", "3.1. Data sets"),
        ("p", f"Mango. The public Mango DMC and NIR spectra data set (version 5, file v4) {C('mango_data')} contains "
              f"{N['mango_spectra']} short-wave NIR absorbance spectra (285–1200 nm, 3 nm steps) of {N['mango_fruit']} "
              f"intact mango fruit with dry-matter content (DM, % w/w) reference values, collected over seven harvest seasons "
              f"(2015–2021) with {N['mango_instruments']} individual spectrometer units (instrument identifiers in the data set), {N['mango_pops']} "
              f"populations (orchard and harvest-date lots) and ten cultivars {C('anderson2020', 'anderson2021')}. "
              "Many fruit were scanned several times and on several instruments (on average 8.1 spectra per fruit)."),
        ("p", f"Soil. The Open Soil Spectral Library v1.2 {C('safanelli2025')} provides visible-NIR reflectance "
              f"spectra (400–2500 nm) and organic carbon (OC) for the LUCAS topsoil survey {C('orgiazzi2018')} "
              f"({N['lucas_n']} samples from the 2009 and 2015 campaigns) and the USDA KSSL library "
              f"({N['kssl_n']} samples with OC and spectra after quality filtering)."),
        ("p", f"Corn and tablets. The corn data set {C('corn_data')} contains 80 ground-corn samples measured on three "
              "NIR spectrometers (m5, mp5, mp6; 1100–2498 nm) with moisture, oil, protein and starch values. The "
              f"IDRC 2002 pharmaceutical tablet shoot-out data {C('tablet_data')} contain 655 tablets measured on two "
              "spectrometers (600–1898 nm) with their official calibration (155), validation (40) and test (460) sets; "
              "the active-ingredient assay was modelled."),
        ("h2", "3.2. Deployment-shift scenarios and leakage control"),
        ("p", "Each scenario holds out complete groups (Table 1). Mango: leave-one-season-out (7 folds), forward "
              "prediction of each season from all earlier seasons (2017–2021), leave-one-instrument-out for the "
              f"{N['mango_inst_tasks']} instruments with ≥ 300 fruit, and grouped 10-fold splitting of populations. Soil: "
              "leave-one-region-out over 30 spatial blocks obtained by k-means clustering of LUCAS coordinates "
              f"(spatial blocking {C('roberts2017')}), and two stress tests, LUCAS 2009 ↔ 2015 campaigns and KSSL → LUCAS "
              "across libraries, instruments and continents. Corn: leave-one-instrument-out, repeated ten times with "
              "20 randomly chosen test samples. Tablets: instrument 1 calibration applied to the instrument-1 test set "
              "(exchangeable control) and to the instrument-2 test set (instrument shift without group information)."),
        ("p", "Leakage control was enforced in code by an assertion in every outer and inner split: a physical unit "
              "(fruit, soil sample, corn sample, tablet) never appears in both a training set and the set it predicts. "
              "This matters in practice: 7100 mango fruit were scanned on more than one instrument, and the corn and "
              "tablet samples were measured on every instrument, so instrument-wise splitting without unit exclusion "
              "would leak the reference value of the test sample into training. All preprocessing is row-wise "
              "(no parameters estimated across samples) and fixed a priori per data set: Savitzky–Golay second "
              f"derivative (window 13, 684–990 nm) for mango {C('savitzky1964')}; absorbance log(1/R) at 10 nm steps "
              f"and first derivative (window 11) for soil; SNV {C('barnes1989')} followed by first derivative (window 15) "
              "for corn and tablets. Soil OC was modelled as log(1 + OC) and interval end-points were "
              "back-transformed, which preserves coverage exactly."),
        ("h2", "3.3. Interval methods compared"),
        ("p", "All PLS-based methods share the same preprocessing, the same number of latent variables (selected by "
              "group-wise cross-validation in the training data) and the same final model, so differences arise from "
              "the uncertainty calibration only. Baselines: (a) the classical interval ŷ ± t·RMSECV·√(1 + h) "
              f"{C('astm1655')} with random cross-validation (ASTM-R) or with group-wise cross-validation (ASTM-G); "
              f"(b) bagged PLS {C('breiman1996')} with bootstrap variance plus out-of-bag residual variance (BAG); "
              f"(c) Gaussian-process regression on PLS scores {C('rasmussen2006')} (GPR, 1000-sample subset); "
              f"(d) quantile gradient boosting {C('ke2017')} on PLS scores and diagnostics (QGB) and its conformalised "
              f"version CQR {C('romano2019')}; (e) split conformal prediction with a random 75/25 unit-wise split (SCP) "
              f"{C('lei2018')}; (f) normalised split CP with k-nearest-neighbour difficulty (NCP-kNN) "
              f"{C('papadopoulos2011')}; (g) CV+ with random unit-grouped folds {C('barber2021', 'lin2022')}; and "
              f"(h) weighted split CP under covariate shift {C('tibshirani2019')}, with the density ratio estimated by "
              "logistic regression between calibration spectra and the unlabelled spectra of the deployment group (WCP; "
              "this method uses test spectra transductively). The proposed GC-D was compared with the guaranteed "
              "variants HCP and HJ+ (Section 2.4), with GC-D plus the finite-sample point mass at +∞ (GC-D+), and with "
              "an oracle that calibrates split CP on labelled spectra of the test group itself (2-fold within the "
              "group; not available in practice, reported as a reference for the attainable width)."),
        ("p", "The factorial ablation crosses three components of GC-D: calibration folds that are random (R) or "
              "out-of-group (G); uniform (U) or group-balanced (W) weights; and absolute (A) or diagnostic-normalised "
              "(D) scores. GC-D corresponds to G-W-D; R-U-A is ordinary cross-conformal calibration."),
        ("h2", "3.4. Evaluation and statistics"),
        ("p", "Primary end-points (fixed in advance) at α = 0.10 were the group-averaged empirical coverage on held-out "
              f"groups and the mean interval (Winkler) score {C('gneiting2007')}"),
        ("eq", "IS_α(l, u; y) = (u − l) + (2/α)(l − y)·1(y < l) + (2/α)(y − u)·1(y > u)", "6"),
        ("p", "a proper score that rewards narrow intervals and penalises misses in proportion to their size. "
              "Secondary end-points were mean width, worst-group coverage, the share of groups with coverage below "
              "0.85, and results at α = 0.05 and 0.20. Three hypotheses were pre-specified: H1, random-split SCP "
              "covers less than 0.85 on at least one shift task; H2, GC-D covers between 0.87 and 0.95 on every task "
              "with ≥ 10 training groups; H3, diagnostic normalisation lowers the interval score relative to "
              "absolute scores (GC-D vs G-W-A). The unit of analysis for method comparisons is the held-out group; "
              f"per-group values were averaged over five pre-specified seeds (0–4) and compared with two-sided Wilcoxon "
              f"signed-rank tests {C('wilcoxon1945')} with Holm correction across comparators within each task "
              f"{C('holm1979')}. Effect sizes are matched-pairs rank-biserial correlations {C('kerby2014')}; 95 % "
              "confidence intervals of group-averaged coverage are percentile bootstraps over groups, and within-task "
              "pooled coverage intervals use a cluster bootstrap over physical units."),
        ("h2", "3.5. Software and reproducibility"),
        ("p", f"All code is in Python (NumPy, SciPy, scikit-learn {C('pedregosa2011')}, LightGBM {C('ke2017')}, "
              f"PyTorch {C('paszke2019')}). PLS1 was implemented with NIPALS and checked against scikit-learn to 10⁻¹⁴. "
              "A single command (python run_all.py --mode full) downloads the data, runs every experiment and "
              "regenerates all tables, figures and the statistics files from which every number in this paper is "
              "read; all computations ran on a 4-core CPU without a GPU."),
    ]
