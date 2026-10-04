# Review round 1 — Reviewer #1 (general, hostile but fair; Talanta)

Manuscript version reviewed: draft v1 (built 2026-10-04 from the results of 12 scenarios × 5 seeds).

| # | Issue | Severity | Fix | Status |
|---|---|---|---|---|
| 1.1 | Title "Prediction intervals that stay valid…" over-claims: GC-D has no finite-sample guarantee in the few-group regime, and the corn and KSSL→LUCAS results show failures. | MAJOR | Retitled: "Group-conformal calibration of near-infrared prediction intervals for new seasons, instruments and regions using PLS diagnostics". Abstract states the limits (≥ ~10 groups for guarantees; no rescue of uncorrected instrument transfer). | Fixed |
| 1.2 | The number of latent variables is chosen on the same out-of-group residuals that are then used as conformity scores (re-use of data). | MAJOR | Quantified in the sensitivity analysis: A ± 4 changed new-season coverage of GC-D only within 0.884–0.898 (Table S5); stated in Section 3/4.5. Selection of 1 of ≤ 25 values has a negligible effect on a quantile estimated from tens of thousands of residuals. | Fixed (evidence + text) |
| 1.3 | Weighted CP is implemented without weight stabilisation; reviewers may regard the baseline as unfair, since it returns unbounded intervals. | MAJOR | Added WCP-clip (density ratios normalised and capped at 20) for all 12 scenarios × 5 seeds (Table S8); discussed in Section 4.1. | Fixed (experiment run) |
| 1.4 | No connection to the analytical-chemistry notion of measurement uncertainty. | MODERATE | GUM (JCGM 100:2008) cited in the Introduction; prediction intervals framed as sample-specific uncertainty statements. | Fixed |
| 1.5 | Supplementary tables cited in the text (S2, S5–S8) did not exist. | MODERATE | Supplementary Material generated automatically (Tables S1–S14, Figs. S1–S2) with numbering matching the text. | Fixed |
| 1.6 | Bagging and quantile-boosting settings not stated. | MINOR | B = 25 unit-level bootstrap models; 300 trees, learning rate 0.05, 31 leaves added to Section 3.3; all settings in Table S1. | Fixed |
| 1.7 | Table 2 combined coverage and score in one cell ("a / b"), hard to read. | MINOR | Split into Table 2 (coverage) and Table 3 (interval score). | Fixed |
| 1.8 | Phrase "within 0 % of the oracle" (rounding artefact). | MINOR | Rephrased with a computed threshold ("less than 1 %"). | Fixed |
