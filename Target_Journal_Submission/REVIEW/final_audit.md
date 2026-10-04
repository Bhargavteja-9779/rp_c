# Final audit (Phases 34–36, 40): consistency, claims, citations, reproducibility

Date: 2026-10-04. State audited: branch `claude/jolly-albattani-qiez8b` after review round 10.

## 1. Automated consistency audit of the manuscript (`manuscript/audit_manuscript.py`)

**33 / 33 checks passed** (`REVIEW/final_audit_checks.json`). The checks recompute from the raw data or the
generated content, and verify:
* the data counts quoted in the text: 85,401 mango spectra; 10,560 fruit; 31 instruments; 199 populations;
  10 cultivars; seasons 2015–2021; 7,100 fruit on more than one instrument; 8.1 spectra per fruit; 24 instruments
  with ≥ 300 fruit; LUCAS 40,175; KSSL 19,747; 30 LUCAS blocks; 146,873 spectra in total; 655 tablets
  (155/40/460); 80 corn samples × 3 instruments; the identity of population 114500;
* the structure: Section 4 subsections, figures and tables are numbered consecutively; every cited figure and table
  exists; supplementary tables are cited only within S1–S15; no "nan" appears in the text;
* the citations: every citation number has a reference and every reference (54) is cited; every figure file exists.

Every result number in the text, tables, supplementary material, cover letter and graphical abstract is generated
from the result files by code (`text_results.py`, `make_tables.py`, `build_supplementary.py`, `build_letters.py`,
`make_graphical_abstract.py`). No result number is typed by hand.

## 2. Cross-document consistency

| Check | Method | Result |
|---|---|---|
| Numbers quoted in REVIEW/*.md, README and the iteration log appear in the result files | Script: every 3-decimal / 2-decimal number in these files matched against all values in `results/**/*.csv` and `tables/*.csv` | All found |
| Abstract ↔ Table 2 ↔ cover letter ↔ graphical abstract | Same generator functions on `summary_results.csv` | Consistent by construction; spot-checked in the rendered PDF (SCP 0.78–0.83; GC-D 0.88–0.90, 0.88, 0.90) |
| Title identical in manuscript, supplementary, cover letter, README | grep | Consistent (README was outdated → fixed in round 10) |
| Hypotheses H1–H3 (protocol) ↔ results ↔ text | `hypotheses.json` | H1 supported, H2 supported, H3 partly supported; the text uses the same wording |
| Post-hoc H4/H5 (iteration log, written before the run) ↔ Section 4.10 | `iteration1_*.csv` | H4 not supported, H5 supported; labelled post-hoc in 4.10, the limitations, Table S7 and the iteration log |
| Claim → evidence | `claim_evidence_audit.md` | 17 claims; all verified; 4 weakened, 1 removed during the audits |
| Citations | `citation_audit.md`, `references_verified.json` | 54 cited references; DOIs, arXiv IDs and Crossref metadata verified; corrections recorded |
| Figures and tables | Visual check of every rendered page (30 manuscript pages, 23 supplementary pages) | Fig. S2 label overlapped a bar → moved. Supplementary Table S14 printed the internal ranking stand-in for an infinite interval score (−999999998.18) where a comparator's intervals were unbounded → now printed as −∞/∞ and explained in the caption; headers shortened. No other overlap, truncation or artefact |
| Journal facts | `journal_selection/` | Talanta, 2025 JIF 6.7, Q1; measured median acceptance time 66 d (all papers), 74.5 d (chemometrics/ML) reported as historical figures, not promises |

## 3. Reproducibility audit ("a stranger with the repository")

Steps a newcomer would take, executed on this machine from clean output directories:

1. **Data.** `scripts/download_data.py` verified all raw files against their SHA-256 checksums. Pass.
2. **Unit tests.** `pytest -q tests`: 8 passed (PLS vs scikit-learn, jackknife+ solver vs brute force, unit-disjoint
   folds, hierarchical coverage on synthetic data). Pass.
3. **Quick mode.** `python run_all.py --mode quick --workers 4` from empty `results_quick/`, `figures_quick/`,
   `tables_quick/`: every step completed in 779 s (13 min), **except the last** — `make_graphical_abstract.py`
   crashed (IndexError) because it expected scenarios that quick mode does not run. The audit also found that the
   script **wrote to `code/figures/` regardless of `FIG_DIR`**, so it would have overwritten the reported graphical
   abstract with quick-mode numbers (it did not this time, because it crashed before saving). **Fixed:** the script
   honours `FIG_DIR` and skips missing scenarios. Re-running the step in quick mode: pass. All other scripts were
   checked for hard-coded output paths: none found. The full results were verified to be untouched (timestamps; `git status`).
4. **Exact re-run of full jobs.** `run_main.py` re-run from scratch for mango new season (seed 0, 462 group × method
   rows) and corn protein (seed 0, 1,980 rows) into a separate results directory:
   * corn protein: identical (maximum absolute difference 0 for coverage, width, interval score, RMSE);
   * mango new season: identical for all methods except GPR, whose interval score differed by ≤ 1.8 × 10⁻⁴
     (BLAS floating-point non-associativity; the original used one thread per process, the re-run two).
   The audit also found that a fresh `run_main.py` included **WCP-clip**, which was added to the method registry
   after the main runs and is evaluated by its own script (`run_wcp_clip.py`). A fresh full run would have added
   WCP-clip rows to the main per-group files and changed the Holm families of the main comparisons. **Fixed:**
   WCP-clip is excluded from the `run_main.py` default, like the post-hoc methods.
5. **Documentation.** README covers installation, data licences (LUCAS not redistributable), commands, measured
   cost (≈ 42 core-hours from the log time stamps), the mapping from manuscript element to script and file,
   leakage control and seeds. `config/experiment_config.json` holds all fixed settings (also Table S1).

## 4. Package manifest (`/Target_Journal_Submission/`)

| Required | Present |
|---|---|
| journal_selection/ | selected_journal.md, journal_comparison.md, journal_verification.md, acceptance_time_table.md, raw acceptance-time data, scripts, JCR evidence |
| manuscript/ | Final_Manuscript.docx, Final_Manuscript.pdf, cover_letter.docx, highlights.docx, build scripts, verified references |
| code/ | src/, experiments/, scripts/, tests/, config/, run_all.py, README.md, requirements.txt, environment.yml |
| results/ (→ code/results) | raw_results.csv, metrics.json, statistics.json, hypotheses.json, summary/per-group/comparison CSVs, experiment_logs/, main/, iteration1/, robustness/, cnn/, cultivar/, wcp_clip/, error_analysis/, decision/, timing |
| figures/ (→ code/figures) | Figs. 1–9 (files fig1–fig9 incl. fig7_efficiency = Fig. S2), fig10 (Fig. S1), graphical abstract; PNG + PDF |
| tables/ (→ code/tables) | all tables as CSV + Markdown |
| supplementary/ | Supplementary_Material.docx/.pdf (Tables S1–S15, Figs. S1–S2), research_process/ (candidate directions, novelty map, pre-registered protocol, iteration log) |
| REVIEW/ | review_01 … review_10, claim_evidence_audit.md, citation_audit.md, rejection_risk_report.md, final_audit.md, final_audit_checks.json |

Not committed by design: raw data (licence, size), per-spectrum Parquet files (≈ 1 GB; regenerated by run_all.py),
per-fold resume caches (`*/partial/`).

## 5. Items that cannot be completed by the analysis (author actions before submission)

Author names, affiliations, ORCID iDs, corresponding-author details, CRediT roles, funding, competing-interest
confirmation, adaptation of the generative-AI declaration, repository DOI (e.g. Zenodo), suggested reviewers.
These are marked `[...]` in the manuscript and cover letter.

## 6. Audit verdict

No remaining inconsistency between data, results, text, figures, tables and documentation was found after the
fixes above. The package is internally consistent and reproducible.
