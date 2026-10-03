# Pre-specified experimental protocol (written before any held-out evaluation)

Date fixed: 2026-10-03 (git history of this file is the timestamp).

## Hypothesis
Prediction intervals for NIR calibration models that are calibrated on randomly split (sample-exchangeable) data
under-cover when the model is deployed on a new group (new harvest season, new instrument, new country). Calibrating
conformal scores *out-of-group* with group-balanced weights, and scaling them by PLS spectral diagnostics, restores
near-nominal coverage on new groups at a moderate width cost.

## Research questions → experiments
| RQ | Question | Experiment |
|---|---|---|
| RQ1 | How much do existing interval methods miscover under group shift? | E1 main + E2 baselines |
| RQ2 | Does group-structured conformal calibration restore near-nominal coverage, and at what width cost? | E1, E2 |
| RQ3 | Which components matter (out-of-group scores, group weights, diagnostic normalisation)? | E3 ablation |
| RQ4 | Robustness to number of training groups, training size, spectral perturbation, α, base model | E4 robustness, E7 sensitivity |
| RQ5 | Does it generalise across domains/datasets and shift types? | E5 generalisation |
| RQ6 | What does it cost computationally? | E6 efficiency |
| RQ7 | Where and why does it fail; what are the decision consequences? | E8 error analysis, E9 decision analysis |

## Pre-specified hypotheses (tested, results reported whatever the outcome)
* H1: random-split split-conformal (SCP) has group-averaged coverage < 0.85 (nominal 0.90) on at least one shift task.
* H2: the proposed method has group-averaged coverage in [0.87, 0.95] on every shift task with ≥ 10 training groups.
* H3: diagnostic normalisation lowers the mean interval score relative to the same method with absolute residual scores (paired over held-out groups).

## Primary endpoints (α = 0.10)
1. Group-averaged empirical coverage on held-out groups (each group weighted equally).
2. Mean interval (Winkler) score, IS_α = (u−l) + (2/α)(l−y)1{y<l} + (2/α)(y−u)1{y>u}.
Secondary: mean width, worst-group coverage, share of groups with coverage < 0.85, coverage at α = 0.05 and 0.20.

## Units, splits, leakage control
* Mango (Anderson et al., Mendeley 10.17632/46htwnp833.5, v4 file): unit = spectrum; reference = fruit (`reference_no`).
  - Season shift: leave-one-season-out (LOSO, 7 folds) and forward-chaining (train < s, test s; s = 2017…2021).
  - Instrument shift: leave-one-instrument-out for instruments with ≥ 300 fruit; **training excludes every fruit that has any spectrum on the test instrument**.
  - Population shift: grouped 10-fold over the 199 populations.
* OSSL vis-NIR: unit = soil sample (`id.layer_uuid_txt`), target = organic carbon (`oc_usda.c729_w.pct`), LUCAS subset.
  - Region shift: leave-one-country-out for countries with ≥ 300 samples.
  - Cross-library: KSSL → LUCAS (single shift, no group guarantee, reported as stress test).
* Corn (Eigenvector, 80 samples × 3 instruments, 4 analytes): leave-one-instrument-out, **sample-disjoint** (test-instrument samples never seen on any instrument in training) using 5 random sample partitions.
* Shootout-2002 tablets (Eigenvector): instrument 1 → instrument 2 with the official calibration/test partition; random-split exchangeable control.
* All preprocessing and model selection inside training folds only. Number of PLS latent variables chosen by inner group-wise CV.

## Methods compared (identical base model and preprocessing for all PLS-based methods)
Classical PLS interval (ASTM E1655-type, t·SEC·√(1+h)); bagged-PLS interval; Gaussian-process regression on PLS scores;
quantile gradient boosting (raw) and CQR; split CP (random); normalised split CP (random, kNN difficulty);
CV+ / jackknife+ (random folds); weighted CP with classifier density ratio using unlabelled target spectra;
proposed group-conformal variants; oracle CP calibrated on labelled target data (reference only).

## Seeds
Pre-specified seeds {0, 1, 2, 3, 4} for every stochastic component. No seed selection after viewing results.

## Statistics
Unit of analysis for method comparisons = held-out group. Paired two-sided Wilcoxon signed-rank tests on per-group interval
score and on per-group |coverage − 0.90|; Holm correction within each task family; effect size = matched-pairs
rank-biserial correlation; 95 % bootstrap CIs over groups. Within-group coverage CIs: cluster bootstrap over fruit/sample.

## Development data
Method design choices (score features, difficulty model form) were explored only on mango seasons 2015–2017.
Results are additionally reported separately for test seasons 2018–2021 ("untouched") to detect development overfitting.
