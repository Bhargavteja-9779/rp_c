# Journal verification evidence

## 1. JCR quartile and Impact Factor
Source: Clarivate JCR export "Journal Data Filtered By: Selected Categories: CHEMISTRY, ANALYTICAL; Selected JCR Year: 2025",
publicly posted by Universidad Complutense de Madrid (https://www.ucm.es/quimica_analitica/file/anal-chem-jcr-journalresults-08-2026).
The extracted text is saved in `evidence/jcr_chemistry_analytical_ucm_2026.txt`. Relevant rows (verbatim values):

| Journal | Publisher | 2025 JIF | Quartile | JCI |
|---|---|---|---|---|
| TALANTA | Elsevier | 6.7 | Q1 | 1.53 |
| Analytica Chimica Acta | Elsevier | 6.1 | Q1 | 1.43 |
| Analytical Chemistry | ACS | 7.3 | Q1 | 1.70 |
| Biosensors & Bioelectronics | Elsevier | 11.8 | Q1 | 2.19 |
| Sensors and Actuators B | Elsevier | 8.3 | Q1 | 1.77 |
| Microchemical Journal | Elsevier | 5.2 | Q1 | 1.17 |
| Chemometrics and Intelligent Laboratory Systems | Elsevier | 3.8 | **Q2** | 1.05 |

Other journals (official journal "About" pages, Oxford Academic): Briefings in Bioinformatics 2025 JIF 7.3, rank 4/85
Biochemical Research Methods (Q1); Bioinformatics 2025 JIF 5.5, rank 7/67 Mathematical & Computational Biology (Q1).

## 2. Acceptance timeline (measured, not reported)
Method: `scripts/acceptance_times.py`, `scripts/acceptance_times_round2.py`, `scripts/acceptance_times_subset.py`.
For each journal we retrieved up to 300 recent research articles (PubMed, publication date ≥ 2025-06-01, reviews excluded)
and computed accepted − received from the publisher-deposited PubMed `<History>` dates. For journals not in PubMed we used
Crossref `assertion` metadata (Springer deposits these; Elsevier does not). Raw outputs: `acceptance_times*.json`; table:
`acceptance_time_table.md`.

Caveats:
* "received" is the first submission date recorded by the publisher. Manuscripts that were rejected and resubmitted may receive a new "received" date, which can understate the true total time.
* These are **submission → acceptance** times, distinct from first-decision time (which Elsevier/OUP advertise and which is much shorter, e.g. Briefings in Bioinformatics advertises an 8-day median first decision while its measured median submission → acceptance is 124 days).
* Acceptance → online publication time was not measured.
* Acceptance rates were not verifiable from official sources and are not reported.

## 3. Legitimacy
Talanta: founded 1958, Elsevier, SCIE-indexed, Q1 in the 2025 JCR, not on any hijacked/predatory journal list we are aware of.
No Clarivate "on hold"/de-listing notices were found for Talanta.
