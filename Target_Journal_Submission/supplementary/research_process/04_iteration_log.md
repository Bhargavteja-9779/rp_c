# Iteration log (Phase 19) — post-hoc changes are labelled as such in the manuscript

## Iteration 1 (written 2026-10-03, before running the experiment)
**Observation (partial seed-0 results):** on the soil task (LUCAS, new region) CQR and GPR have clearly lower interval
scores than GC-D (≈ 8 vs ≈ 10.4 on the first completed fold), while coverage of GC-D is adequate. On mango, GC-D is
competitive. SOC residuals are strongly heteroscedastic in the analyte level (organic soils), a dependence that the
diagnostic scale σ(T², Q) cannot represent.

**Hypothesis H4 (post-hoc):** adding the predicted value ŷ (in the modelling scale) to the scale model,
σ(T², Q, ŷ), lowers the interval score on tasks with level-dependent error (soil), without loss of coverage on the
other tasks.

**Hypothesis H5 (post-hoc):** the out-of-group calibration principle is score-agnostic. Computing CQR conformity
scores out-of-group with group-balanced weights ("GC-CQR") keeps CQR's adaptivity while restoring coverage under
group shift where random-split CQR under-covers (mango instrument).

**Experiment:** methods GC-D2 and GC-CQR added; rerun on all main tasks, α = 0.1, seeds 0–2 (reduced from 0–4 for computing time; post-hoc analysis), compared with GC-D,
CQR, SCP under the same statistics. Results reported whether positive or negative.

## Bug found and fixed during the robustness experiment (2026-10-04)
The first run of the test-time perturbation experiment (E4c) perturbed *all* spectra of the mango data set
(every spectrum is a test spectrum in some leave-one-season-out fold), so the training spectra of each fold were
perturbed as well. Because PLS predictions are invariant to a common scaling, the "gain" perturbation showed no
effect at all, which exposed the bug. The experiment was corrected to perturb only the test spectra of the
current fold (with an assertion that training spectra are unchanged) and rerun; the invalid results were deleted.
