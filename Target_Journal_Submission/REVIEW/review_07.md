# Review round 7 — Reviewer #7 (scientific writing, logic, terminology, figures/tables, author guidelines)

Reviewed the full text of draft v2 (plain-text dump `_render/draft_v2.txt`) and the rendered DOCX/PDF.

| # | Issue | Severity | Fix | Status |
|---|---|---|---|---|
| 7.1 | Undefined abbreviations at first use: RMSEP, RMSECV, LOSO; "Q-residual ratio" in Fig. 7 never defined. | MODERATE | Defined in Sections 3.2–3.3 and 4.8. | Fixed |
| 7.2 | Inline symbols with underscores (Y_new, N_g, R_A, μ̂₋ₖ) rendered literally in the DOCX; equations bypassed the markup parser. | MODERATE | Subscript markup applied throughout; equation renderer now parses markup (Cambria Math). | Fixed |
| 7.3 | H2 task list printed as "(mango, new instrument, mango, new population, soil, new region)". | MINOR | Semicolon-separated scenario names. | Fixed |
| 7.4 | Section 4.4 stated "6 training seasons, 2 corn instruments or 2 earlier seasons" — incorrect for forward folds (2–6 earlier seasons). | MINOR | "With at most six training seasons or two corn instruments". | Fixed |
| 7.5 | "Nearly uninformative" for corn contradicted by the minimum RMSEP/SD ratio 0.61. | MINOR | Median ratio and maximum instrument bias reported; wording "weakly informative". | Fixed |
| 7.6 | Pooled coverage of GC-D (0.927) above nominal is not explained. | MINOR | Explained as over-coverage of large seasons resembling the calibration data (2016: 0.970, 2017: 0.972). | Fixed |
| 7.7 | Theory Step 4 did not say that T² and Q of a test spectrum come from the final model. | MINOR | Stated. | Fixed |
| 7.8 | Statistics section did not describe the outer-fold unit used for populations/campaigns (introduced in round 3). | MINOR | Added to Section 3.4. | Fixed |
| 7.9 | Section numbers 4.7 and 4.10 missing in draft v2 because their results (timing, post-hoc iteration) were not yet available. | MINOR | Final build after all experiments; section-number audit in final_audit.md. | Pending final build |
| 7.10 | Talanta submissions require highlights (3–5 bullets, ≤ 85 characters) and a graphical abstract. | MODERATE | Created (manuscript/highlights.docx, graphical abstract figure). | Fixed (see round 9) |
| 7.11 | Ten figures is heavy for a full paper; Fig. 7 (computing cost) and Fig. 10 (effect sizes) duplicate tables. | MINOR | Moved to Supplementary (Figs. S1–S2); main text has 8 figures and 4 tables. | Fixed |
