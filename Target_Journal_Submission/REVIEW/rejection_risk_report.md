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
| 5 | **Reproducibility**: long run time (≈ 1 day on 4 cores); LUCAS data licence prevents redistribution. | run_all.py, README. | Low | Download script with checksums; quick mode (~15 min); resumable full mode; all result files included. | Fixed |
| 6 | **Baselines**: GPR on a 1000-sample subset, untuned quantile GBM, WCP without clipping (now added), no calibration-transfer baseline. | Section 3.3, Table S8. | Medium | WCP-clip added; settings disclosed; GPR/CQR remain strongest on soil (no sign of weakening); calibration transfer discussed as complementary. | Partly |
| 7 | **Generalisation**: exchangeability of groups is assumed; a new instrument *type* or a trend is not covered; per-group coverage varies widely (worst groups ≪ 0.90 for every method). | Fig. 4, Section 4.8, cultivar test. | Medium | Forward-chaining test, cultivar test, worst-group statistics (Table S4), error analysis. | Mitigated |
| 8 | **A simpler alternative** (classical interval with group-wise RMSECV, ASTM-G) achieves similar coverage. | Section 4.2, Table 2. | **Medium–High** | Reported openly; positioned as part of the main message; GC-D's added value (sharper intervals, drift adaptivity, guarantees with many groups) quantified. | Mitigated (honest) |
| 9 | **Writing**: dense quantitative text, many abbreviations; ~5,400 words. | Draft. | Low–Medium | Review round 7 edits; abbreviations defined; two figures moved to the supplement. | Mostly fixed |
| 10 | **Formatting**: author names, affiliations, ORCID, funding, repository DOI, suggested reviewers are placeholders. | Manuscript, cover letter. | High if submitted as is | Must be completed by the authors before submission. | **Open (author action)** |
| 11 | **Citations**: two 2026 preprints (SSRN, arXiv) and one ACM JDS 2026 article are very recent; the SSRN preprint's content could not be inspected. | citation_audit.md. | Low | Cited at title level only; all DOIs/arXiv IDs verified. | Mitigated |
| 12 | **Scope**: an editor may judge the work as statistics/chemometrics with limited analytical-chemistry content (desk rejection). | Talanta scope: novelty + analytical applicability on real samples. | Medium | Real samples from four matrices; decision analysis with specification limits; link to measurement uncertainty (GUM); cover letter argues fit. Backup journal: Analytica Chimica Acta. | Mitigated |
| 13 | **Integrity/compliance**: AI-assisted preparation must be declared; post-hoc analyses must be labelled; the timeline target (≤ 72 days to acceptance) cannot be guaranteed. | Declarations; Section 4.10; journal_selection. | Low | AI declaration included; post-hoc analyses labelled; measured median acceptance time reported as a historical figure only. | Fixed |

**Overall**: the main residual risks are novelty perception (1), statistical strength of pairwise differences (4) and the
strong simple alternative (8). They are inherent to the findings and are disclosed rather than hidden. The remaining
blocking items are author actions (10).
