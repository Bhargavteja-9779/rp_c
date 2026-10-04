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

## Iteration 1 — outcome (2026-10-04, after the run; seeds 0–2, 27 jobs)
* **H4 not supported.** GC-D2 had a lower median interval score than GC-D in 6 of 9 scenarios, none significant after
  Holm correction; its mean interval score on new soil regions was *higher* (13.53 vs 11.90) and coverage unchanged.
  GC-D2 is not adopted; GC-D remains the proposed method.
* **H5 supported.** GC-CQR restored CQR coverage under group shift (mango instrument 0.770 → 0.900, next season
  0.727 → 0.858, new season 0.788 → 0.901) and had the lowest soil interval score of all methods (7.77 vs CQR 8.04,
  Holm p < 0.001). Its median IS was lower than CQR's in 8/9 scenarios (Holm p < 0.05 in 4: corn oil, corn protein, mango instrument, soil). Caveats: on new mango
  instruments it is less sharp than GC-D (6.36 vs 6.21), and on corn its coverage (0.81–0.90) is below CQR's.
* Both variants were designed after seeing the data and are reported in the manuscript as post-hoc (Section 4.10,
  Supplementary Table S7, limitations). They require independent confirmation.

## Timing experiment repeated on an idle machine (2026-10-04)
The first run of the isolated timing experiment (E6, `run_timing.py`) was started while the 27 post-hoc iteration
jobs were still running, so wall times were inflated by CPU contention. It was stopped, its outputs were deleted,
and it was re-chained (`scripts/after_iteration.sh`) to start only after the iteration jobs had finished. Only the
idle-machine run is reported (Section 4.7, Table S9, Fig. S2). Per-method times from the main runs are never used,
because memoised shared components make them incomparable between methods.
