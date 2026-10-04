# Review round 10 — Final adversarial review (simulated "reject" reviewer, whole package)

Manuscript version reviewed: the final build after rounds 1–9, with all experiments complete (main 60 jobs, post-hoc
27 jobs, robustness, CNN, WCP-clip, cultivar, isolated timing). The reviewer was told to find the single strongest
reason to reject and then every remaining weakness, re-reading the manuscript against the result files rather than
against earlier reviews.

## Strongest reason to reject (would an editor accept it?)

> "The proposed method is not needed: a classical PLS interval whose RMSE is estimated by group-wise rather than random
> cross-validation (ASTM-G) achieves the same coverage. GC-D is hierarchical conformal prediction plus a known
> normalised score. The contribution is therefore an observation (validate group-wise) that chemometricians already know."

**Assessment.** This is the most dangerous criticism and it cannot be removed, only answered. The answer in the
manuscript is (i) the multi-dataset quantification that *current practice* (random-split CP, ASTM-R) under-covers
by 7–12 percentage points under realistic deployment shift, which is not documented for NIR in the literature found
(novelty map); (ii) GC-D had a lower interval score than ASTM-G in all four main scenarios (5.90 vs 6.18, 6.14 vs
6.73, 6.21 vs 6.48, 11.90 vs 12.39), kept coverage under a 2-nm wavelength shift (0.938 vs 0.846 for the unscaled
out-of-group interval), and its guaranteed variants (HCP/HJ+) give finite-sample statements with ≥ 10 groups;
(iii) the borrowed components are named explicitly (Section 4.9).
**Finding 10.0 (MAJOR):** the *abstract* did not mention ASTM-G, so a reader of the abstract alone would over-rate
GC-D. **Fixed:** the abstract now says that a classical interval based on the group-wise RMSECV reached similar coverage
with higher interval scores, and that interval-score gains over SCP were mostly not significant at the group level.
Verdict: not fatal if disclosed, which it now is everywhere (abstract, 4.2, 4.3, conclusions, cover letter, risk 8).

## Major issues

| # | Issue | Check against results | Fix | Status |
|---|---|---|---|---|
| 10.1 | Abstract omitted that interval-score gains are mostly non-significant (Table 4). | comparisons_alpha0.1.csv: GC-D vs SCP Holm p < 0.05 only for soil regions. | Sentence added to the abstract. | Fixed |
| 10.2 | Conclusions generalised "close to nominal coverage for new groups", contradicted by corn (all < 0.83) and KSSL→LUCAS (0.60). | summary_results.csv. | Restricted to "new seasons, instruments and regions in our scenarios with several groups"; the next sentences keep the failure statement. | Fixed |
| 10.3 | Post-hoc Section 4.10 counted "GC-D2 lower in 6 of 9 scenarios" (medians) without saying that none was significant and that the mean soil IS of GC-D2 was *worse* (13.53 vs 11.90) — a misleadingly positive reading of a negative result. | iteration1_comparisons.csv (all GC-D2 vs GC-D Holm p ≥ 0.05). | Paragraph rewritten: significance counts, the higher soil score, and "not supported" stated; for GC-CQR, the instrument IS disadvantage vs GC-D (6.36 vs 6.21) and the corn coverage loss (0.81–0.90 vs CQR) added. | Fixed |
| 10.4 | "The calibration principle is not tied to PLS" from one CNN on one scenario. | cnn_summary.csv (seeds 0–2, 7 seasons). | Weakened to "for this network, at least …". | Fixed |
| 10.5 | GC-CQR beats GC-D on soil; should this not be the proposed method? | GC-CQR soil IS 7.77 vs 11.90, but on mango GC-D ≤ GC-CQR; GC-CQR designed post hoc. | Kept as post-hoc extension (labelled; limitations; independent confirmation required); conclusions mention it as an open direction. Switching the headline method after seeing the data would be HARKing. | Addressed |

## Moderate issues

| # | Issue | Fix | Status |
|---|---|---|---|
| 10.6 | NIR, PLS and RMSECV were not defined in the abstract. | Defined at first use in the abstract (abstract 208 words, below the 250-word limit). | Fixed |
| 10.7 | README cited the old title, an unspecified "several hours" runtime, the old figure numbering and omitted four experiment scripts. | README updated (title, measured ≈ 42 core-hours from log time stamps, figure/table map incl. supplementary, all scripts); run_all.py docstring likewise. | Fixed |
| 10.8 | Quick mode would run the full 3-season timing experiment (~15 min extra). | run_timing.py --quick (one season), used by run_all.py --mode quick. | Fixed |
| 10.9 | Per-group coverage is widely dispersed (worst season 0.798, worst instrument 0.356, worst population 0.013) for every method; the group-averaged coverage hides this. | Already shown in Fig. 4 and Table S4; population 114500 analysed as a bias failure (Section 4.8). No further change. | Addressed (disclosed) |
| 10.10 | The ≈ 1 % noise perturbation breaks all methods (GC-D 0.703; RMSEP 1.38 → 3.50). | Reported in 4.5 with numbers; GC-D degrades least among bounded intervals; ORACLE needs width 11.6. | Addressed (disclosed) |
| 10.10a | Reproducibility audit: `make_graphical_abstract.py` crashed in quick mode and ignored `FIG_DIR` (would overwrite the reported graphical abstract); a fresh `run_main.py` would include WCP-clip, changing the main Holm families. | Both fixed; quick mode passes end to end; re-runs of two full jobs reproduce the committed per-group results exactly (GPR within 2 × 10⁻⁴). Details in final_audit.md §3. | Fixed |
| 10.10b | Supplementary Table S14 printed the ranking stand-in −999999998.18 for unbounded comparators. | Printed as −∞/∞, caption explains; headers shortened. | Fixed |
| 10.11 | Final result folders were git-ignored while experiments ran (iteration1/, robustness/, cnn/, cultivar/, error_analysis/, experiment_logs/). | Temporary ignore entries removed; only `*/partial/` and Parquet files stay ignored. | Fixed |

## Minor issues

| # | Issue | Fix | Status |
|---|---|---|---|
| 10.12 | Section 4.7 (computing cost) and Table S9/Fig. S2 depended on the timing run. | Filled from results/timing_summary.csv after the isolated run; see review_06. | Fixed |
| 10.13 | Claim–evidence rows C13, C15, C17 were "to verify at final build". | Verified and rewritten with numbers (claim_evidence_audit.md). | Fixed |
| 10.14 | Author information, ORCID, funding, repository DOI, suggested reviewers. | Cannot be supplied by the analysis; placeholders clearly marked. | Open (author action) |

## Final proofreading pass (complete read of the rendered PDF)

| # | Issue | Fix | Status |
|---|---|---|---|
| 10.15 | Limitations said "a new cultivar … is not covered", contradicting the leave-one-cultivar-out result (Section 4.6). | Reworded: a trend beyond the variation among past seasons, or a cultivar/instrument type unlike any in the calibration population, is not covered; the tested cultivars were measured in represented seasons and on represented instruments. | Fixed |
| 10.16 | Table 2/3 headers broke mid-word ("Minstrumen t", "Mpopulatio n"). | Labels shortened to M-instr./M-pop. in all tables (abbreviations in the caption). | Fixed |
| 10.17 | Table 1 printed degenerate ranges ("6–6", "120–120"). | A single value is printed when all outer folds agree. | Fixed |
| 10.18 | Fig. 3 caption ("values beyond 3 or infinite are printed") was garbled. | "ratios above 3 and infinite scores are plotted at 3 and labelled" (labels verified in the figure). | Fixed |
| 10.19 | Hyphen-minus in negative numbers (r = -0.39; Table 4). | Typographic minus applied to running text, captions and table cells (not to references/DOIs). | Fixed |
| 10.20 | Comma splice in Section 4.8 ("…at L = 17 %, that of GC-D did not"). | Semicolon. | Fixed |
| 10.21 | Hand-written claim "GC-D over-covered the large seasons (2016, 2017)" checked against per_group_results.csv. | Confirmed (0.970 and 0.972; 15,310 and 27,312 spectra). No change. | Verified |

## Decision of the simulated reviewer after fixes

Major revision → **minor revision / acceptable for review**. The paper is an honest, well-controlled empirical
study with a modest methodological contribution; its value lies in the quantification of under-coverage under
deployment shift and in a practical, drift-sensitive recipe. Rejection remains possible on novelty grounds
(risk 1 and 8 in rejection_risk_report.md), which no further experiment can remove.
