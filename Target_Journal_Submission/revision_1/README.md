# Revision 1 — TAL-D-26-07648 (Talanta), due 18 Nov 2026

Decision: major revision (Reviewer 1: 24 comments; Reviewer 4: 5 comments). Submitted version = git tag `submitted-v1`.

## Files to upload in Editorial Manager

| File | Purpose |
|---|---|
| `Response_to_Reviewers.docx` / `.pdf` | Point-by-point response (every comment quoted verbatim) |
| `response_to_reviewers.md` | Same text as plain Markdown, for pasting into the peer-review platform ("respond to reviews in our peer review platform") |
| `Revised_Manuscript_clean.docx` / `.pdf` | Revised manuscript (also `../manuscript/Final_Manuscript.*`) |
| `Revised_Manuscript_highlighted.docx` / `.pdf` | Revised manuscript with all changes since the submitted version highlighted in yellow |
| `../supplementary/Supplementary_Material.docx` / `.pdf` | Supplementary Material, Tables S1–S28, Figs. S1–S3 (S16–S28 and Fig. S3 new) |
| `../manuscript/highlights.docx` | Highlights (unchanged) |
| Graphical abstract | Your own image from the first submission can be re-used; no reported number changed |

## Decisions only the authors can make (please check before uploading)

1. **CRediT statement** — filled in as: P N Bhargav Teja: Conceptualization, Methodology, Software, Formal analysis, Investigation,
   Data curation, Visualization, Writing – original draft; Divya Meena S: Conceptualization, Supervision, Validation, Project
   administration, Writing – review & editing. Edit `front_and_back()` in `../manuscript/text_results.py` if this is not accurate.
2. **Generative-AI declaration** — it was missing from the submitted file. Elsevier requires it when AI tools were used; it has been
   restored in Elsevier's wording. Review the wording, but do not remove it.
3. **Funding** — no funding statement is included. If the work was funded, add it (Elsevier asks for one; if there was none, the
   usual sentence is "This research did not receive any specific grant from funding agencies in the public, commercial, or
   not-for-profit sectors.").
4. **Zenodo DOI (R1.20)** — the response promises an archive with a DOI. You can reserve a DOI on Zenodo now ("Reserve DOI" when
   creating an upload) and add it to the Data availability statement before resubmitting.
5. **Affiliation** — the author block uses "School of Computer Science and Engineering, Vellore Institute of Technology, Vellore,
   Tamil Nadu, India" (from your submitted title page, with state and country added).

## How the revision was produced

* New experiments: `../code/experiments/run_revision.py` (scale-model form, unequal group sizes, bias correction with k reference
  samples, Q-based rejection rule, WCP variants) and `run_simulation.py` (finite-K study); analyses in `revision_analyses.py`.
  Outputs in `../code/results/revision/`. All are run by `run_all.py`.
* Every number in the manuscript and in the response is read from those files; a check confirmed that all 95 decimal numbers of
  the response occur in the result files, and the manuscript audit (`../manuscript/audit_manuscript.py`) passes 35/35 checks.
* `build_highlighted.py` (in `../manuscript/`) aligns every block of the revision with the submitted version
  (`submitted_v1_content.json`, identical to the tagged submission) and highlights inserted or changed words, changed table cells,
  revised figures and new references; renumbered citations are not marked as changes.
* `build_response.py` builds the response from `reviewer_comments.json` (comments extracted verbatim from the decision letter).
