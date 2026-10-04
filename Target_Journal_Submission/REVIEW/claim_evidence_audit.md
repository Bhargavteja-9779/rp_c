# Claim → evidence audit (Phase 22)

Every quantitative statement in the manuscript is generated from result files by `manuscript/text_results.py`
(and `text_static.py` for data descriptions, verified by `manuscript/audit_manuscript.py`). This table maps the
*claims* (qualitative conclusions) to their evidence.

| # | Claim (location) | Evidence | Experiment | Table / Figure | Citation | Verdict |
|---|---|---|---|---|---|---|
| C1 | Classical PLS intervals and random-split CP under-cover new seasons and instruments (Abstract, 4.1) | SCP 0.783–0.826, ASTM-R 0.788–0.833 on mango season/instrument scenarios; H1 supported | E1/E2 (`run_main.py`) | Table 2, Fig. 3 | – | Supported |
| C2 | Under-coverage is caused by random calibration, not by SCP's smaller training set (4.3) | R-U-A (same final model as GC-D, random folds) 0.795 vs SCP 0.794 for new instruments | E3 ablation | Fig. 5 | – | Supported |
| C3 | GC-D restores near-nominal group-averaged coverage on scenarios with several groups (Abstract, 4.2) | GC-D 0.877–0.899 on mango season/instrument/population and soil region; H2 supported | E1 | Table 2 | – | Supported (empirical, not guaranteed — stated) |
| C4 | GC-D's interval score is close to the oracle's (Abstract, 4.2) | 5.90 vs 5.90 (new season), 6.14 vs 6.36 (next season), 6.21 vs 5.71 (new instrument) | E1 | Table 3 | – | Supported ("close"; instrument 9 % higher stated implicitly by numbers) |
| C5 | GC-D is better than SCP in interval score | Lower in 7/9 main scenarios; significant after Holm only for soil regions | Statistics | Table 4, Table S14 | Wilcoxon, Holm | Weakened in text to "consistent direction, mostly not significant" |
| C6 | Out-of-group calibration supplies most of the gain (Abstract, 4.3) | R-U-A → G-U-A carries most coverage change; ASTM-G (group RMSECV) reaches similar coverage | E3, ASTM-G | Fig. 5, Table 2 | – | Supported |
| C7 | Diagnostic scaling helps under spectral drift (Abstract, 4.5) | 2-nm shift: GC-D 0.938 vs G-W-A 0.846 vs SCP 0.755 | E4c (corrected) | Fig. 6c | – | Supported |
| C8 | Diagnostic scaling lowers the IS in general (H3) | Lower in 5/9 scenarios, significant in 1 | E3 | Fig. 5 | – | Only partly supported — stated |
| C9 | Finite-sample group guarantees need ≈ 10+ groups (Abstract, 2.4, 4.4) | Theory (+∞ mass 1/(K+1) > α); HJ+ unbounded for K ≤ 5, finite from K = 10; HCP unbounded with ≤ 6 seasons | Theory + E4a | Fig. 6a, Table S13 | Lee et al. | Supported |
| C10 | No interval method rescues uncorrected instrument transfer (Abstract, 4.6) | Corn: all PLS-based methods < nominal, RMSEP/SD 0.61–2.45; CQR = marginal range; KSSL→LUCAS RMSEP 23.7 % OC | E1/E5 | Table S12, Table S2 | Feudale; Workman | Supported |
| C11 | GC-D lowers false acceptances in specification-limit decisions (Abstract, 4.8) | L = 16 %: 0.021 vs 0.041 (SCP); L = 17 %: 0.024 vs 0.057; at the cost of lower yield (0.342 vs 0.434) | E9 | Fig. 8, Table S11 | – | Supported (cost stated) |
| C12 | Coverage gap is not a small-sample effect (4.5) | 10–50 % of training fruit: GC-D 0.892–0.898, SCP 0.825–0.832 | E4b | Fig. 6b | – | Supported |
| C13 | Out-of-group calibration also works with a non-PLS point predictor (4.5) | 1D-CNN (seeds 0–2, 7 seasons): SCP 0.651 / IS 8.30; R-U-A 0.646; G-W-A 0.881; GC-D 0.886 / IS 6.11 (σ from PLS diagnostics) | E4d | Table S6 | Cui & Fearn; Mishra & Passos | Supported for one CNN on one scenario — wording limited accordingly (limitations bullet 4) |
| C14 | GC-D costs no sharpness when the shift is small (4.6) | Leave-one-cultivar-out: IS 4.68 vs 4.71 (SCP); populations 4.92 vs 4.96 | E5 (cultivar), E1 | Table S15 | – | Supported |
| C15 | GC-D is computationally cheap (4.7) | Isolated timing (timing_summary.csv) | E6 | Table S9, Fig. S2 | – | To verify at final build |
| C16 | WCP achieves coverage only via unbounded intervals; clipped WCP under-covers (4.1) | WCP finite fraction 0.81 (instr.); WCP-clip 0.851/0.855/0.822 on instrument/season/next season | Reviewer-requested baseline | Table S8 | Tibshirani et al. | Supported |
| C17 | Post-hoc: out-of-group calibration transfers to CQR scores (GC-CQR); a level-dependent scale (GC-D2) does not help (4.10) | GC-CQR coverage: instrument 0.770 → 0.900, next season 0.727 → 0.858; soil IS 7.77 vs CQR 8.04 (Holm p < 0.001); median IS lower than CQR in 8/9 (4 significant); corn coverage 0.81–0.90 below CQR. GC-D2: 6/9 lower medians, none significant; soil mean IS 13.53 vs 11.90 | Post-hoc (seeds 0–2) | Table S7 | Romano et al. | Supported as stated; labelled post-hoc in text, limitations and iteration log; negative result for GC-D2 reported |

Claims removed or weakened during the audit:
* "Prediction intervals that stay valid…" (title) → removed (C3 is empirical, C10 shows failures).
* "GC-D significantly improves the interval score" → replaced by C5 wording.
* "H3 supported" → "only partly supported".
* "the model becomes nearly uninformative" (corn) → "weakly informative" with numbers.
