# Final rejection-risk report (Phase 41)

Target journal: **Talanta** (Elsevier; 2025 JIF 6.7, Q1 Chemistry, Analytical).
No manuscript can be guaranteed acceptance; this report lists the risks that remain after ten review rounds.
Severity: High / Medium / Low (probability × impact on the editorial decision).

| # | Risk | Evidence | Severity | Mitigation | Fixed? |
|---|---|---|---|---|---|
| 1 | **Novelty**: reviewers may regard GC-D as hierarchical CP (Dunn et al.; Lee et al.) plus normalised scores applied to spectra. | Components exist separately (Section 4.9 says so). | **Medium–High** | Contribution framed as (i) multi-dataset evidence of coverage failure of current practice under real deployment shift, (ii) T²/Q-based out-of-group scores that react to drift, (iii) cross-fitting with existing group CV, (iv) group-count requirement; explicit "what is borrowed" paragraph. | Mitigated, not removable |
| 2 | **Methodology**: GC-D has no finite-sample guarantee with few groups; HJ+/HCP need ≥ 10 groups. | Theory (Section 2.4); Fig. 6a. | Medium | Stated prominently (title, abstract, 2.4, limitations); guaranteed variants evaluated. | Mitigated |
| 3 | **Dataset**: the main evidence comes from one fruit data set (mango); the soil region shift is mild; corn/tablets are small. | Tables 2, S2, S12. | Medium | Four data sets, 12 + 1 scenarios; failures reported; cultivar test added. | Partly |
| 4 | **Statistics**: interval-score improvements are mostly not significant at the group level after Holm correction (few seasons). | Table 4, S14. | **Medium–High** | Claims rest on consistent direction and pre-registered coverage criteria H1/H2; exact limits of power stated; effect sizes and uncorrected p reported; outer-fold units where required. | Mitigated (honest), not removable |
| 5 | **Reproducibility**: full run ≈ 42 core-hours as measured from the logs (main 16.7, post-hoc 8.7, robustness 6.9, CNN 9.3, other 0.6), about half a day on 4 cores; LUCAS data licence prevents redistribution. | run_all.py, README §3, experiment_logs/. | Low | Download script with SHA-256 checksums; quick mode exercised end to end (final_audit.md); resumable full mode; all per-group result files and logs committed. | Fixed |
| 6 | **Baselines**: GPR on a 1000-sample subset, untuned quantile GBM, no calibration-transfer baseline; on soil, CQR/GPR beat GC-D in interval score, and the post-hoc GC-CQR beats both. | Section 3.3, 4.10, Tables S7–S8. | Medium | WCP-clip added; settings disclosed; strongest competitors reported as such (CQR/GPR on soil); post-hoc GC-CQR shows the out-of-group principle carries over to CQR scores; calibration transfer discussed as complementary. | Partly |
| 7 | **Generalisation**: exchangeability of groups is assumed; a new instrument *type* or a trend is not covered; per-group coverage varies widely (worst groups ≪ 0.90 for every method). | Fig. 4, Section 4.8, cultivar test. | Medium | Forward-chaining test, cultivar test, worst-group statistics (Table S4), error analysis. | Mitigated |
| 8 | **A simpler alternative** (classical interval with group-wise RMSECV, ASTM-G) achieves similar coverage. | Section 4.2, Table 2, Abstract. | **Medium–High** | Reported openly, now also in the abstract; positioned as part of the main message; GC-D's added value (lower IS than ASTM-G in all four main scenarios, drift adaptivity, guarantees with many groups) quantified. | Mitigated (honest) |
| 9 | **Writing**: dense quantitative text, many abbreviations; ~5,400 words. | Draft. | Low–Medium | Review round 7 edits; abbreviations defined; two figures moved to the supplement. | Mostly fixed |
| 10 | **Formatting**: author names, affiliations, ORCID, funding, repository DOI, suggested reviewers are placeholders. | Manuscript, cover letter. | High if submitted as is | Must be completed by the authors before submission. | **Open (author action)** |
| 11 | **Citations**: two 2026 preprints (SSRN, arXiv) and one ACM JDS 2026 article are very recent; the SSRN preprint's content could not be inspected. | citation_audit.md. | Low | Cited at title level only; all DOIs/arXiv IDs verified. | Mitigated |
| 12 | **Scope**: an editor may judge the work as statistics/chemometrics with limited analytical-chemistry content (desk rejection). | Talanta scope: novelty + analytical applicability on real samples. | Medium | Real samples from four matrices; decision analysis with specification limits; link to measurement uncertainty (GUM); cover letter argues fit. Backup journal: Analytica Chimica Acta. | Mitigated |
| 13 | **Integrity/compliance**: AI-assisted preparation must be declared; post-hoc analyses must be labelled (GC-D2 negative, GC-CQR positive, both on the same scenarios, seeds 0–2); the timeline target (≤ 72 days to acceptance) cannot be guaranteed. | Declarations; Section 4.10; 04_iteration_log.md; journal_selection. | Low | AI declaration included; post-hoc hypotheses written down before the run; negative result reported; measured median acceptance time reported as a historical figure only. | Fixed |

**Overall**: the main residual risks are novelty perception (1), statistical strength of pairwise differences (4) and the
strong simple alternative (8). They are inherent to the findings and are disclosed rather than hidden. The remaining
blocking items are author actions (10).

## Final decision (Phase 42)

**READY for submission to Talanta — scientifically and technically — subject only to the author actions in risk 10**
(names, affiliations, ORCID, funding, competing-interest confirmation, AI-declaration review, repository DOI,
suggested reviewers), which cannot be supplied by the analysis.

Basis: all pre-registered and reviewer-requested experiments are complete (main 12 scenarios × 5 seeds; post-hoc
iteration; robustness, sensitivity, CNN, WCP-clip, cultivar, isolated timing); ten review rounds were addressed;
the manuscript audit passes 33/33 checks; claims are mapped to evidence; citations are verified; negative results
(corn, KSSL→LUCAS, noise, GC-D2, non-significant IS gains, ASTM-G as a strong simple alternative) are reported in
the abstract or results; the reproducibility audit passed after two fixes (final_audit.md).

Acceptance cannot be guaranteed, and neither can acceptance within 72 days: Talanta's measured historical
median is 66 days (all research articles) and 74.5 days (chemometrics/ML papers).
