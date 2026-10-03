# Internal record: candidate research directions (Phase 1–2)

Constraints: target journal Talanta (analytical chemistry, real samples), CPU-only (4 cores, 15 GB RAM, no GPU),
public real data, strong baselines available, objectively testable contribution.

| # | Direction | Data | Main prior art found | Novelty risk | Feasibility | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Coverage-valid prediction intervals for NIR calibrations under deployment shift (new season / instrument / region) using group-structured conformal calibration with spectral diagnostics** | Mango DMC v4 (85k spectra, 7 seasons, 31 instruments), OSSL vis-NIR (LUCAS countries, KSSL), Corn (3 instruments), Shootout-2002 tablets (2 instruments) | CP in chemometrics only under random splits (Jović 2025 Food Chem; Wiens et al. 2026 Anal Chem; Lin et al. 2022 J Chemom; Cui et al. 2026 SSRN preprint); hierarchical CP theory outside chemistry (Dunn et al. 2022 JASA; Lee et al. 2026 ACM JDS) | Moderate: components exist separately in statistics | High | **SELECTED** |
| 2 | Standard-free calibration transfer via optimal transport on PLS scores | Corn, tablets | di-PLS (2018), TCA/CORAL/JDA, many 2020–2026 transfer papers | High (crowded) | High | Rejected: crowded |
| 3 | Tabular foundation models (TabPFN) for NIR calibration | various | arXiv 2605.21544 (2026) already does this | High | Medium | Rejected |
| 4 | Automatic pre-processing ensembles | various | SPORT, PORTO, Mishra et al. | High | High | Rejected |
| 5 | 1D-CNN vs PLS benchmark | Mango | Mishra & Passos 2021; arXiv 2605.02636; SAA 2024 | High | Medium | Rejected |
| 6 | Physics-based spectral augmentation | various | Bjerrum et al. 2017; many | High | High | Rejected |
| 7 | Stable wavelength selection | various | CARS, VCPA, IRIV, GA-PLS… | Very high | High | Rejected |
| 8 | Applicability-domain detection with conformal anomaly detection | Mango, OSSL | partially covered by Q/T² literature | Moderate | High | Merged into #1 (diagnostic normalisation) |
| 9 | Active sample selection for calibration maintenance | Mango seasons | Nikzad-Langerodi et al. 2018 ACA (melamine) | Moderate | Medium | Rejected: weaker evaluation design |
| 10 | Hierarchical mixed-effects PLS across instruments | Mango | multi-domain PLS (Mikulasek et al. 2023 J Chemom) | Moderate | Medium | Rejected |
| 11 | Open-set Raman bacterial identification | Ho et al. 2019 data | many DL papers | High | Low (GPU) | Rejected |
| 12 | LIBS quantification with matrix effects | scarce public data | — | — | Low (data) | Rejected |
| 13 | Hyperspectral image regression uncertainty maps | large cubes | — | Moderate | Low (compute) | Rejected |
| 14 | Temperature-robust NIR models | Wülfert data (small) | Sun et al. 2020 PBT; EPO/GLSW | High | High | Rejected: small data, crowded |
| 15 | Joint conformal regions for multiple analytes | Corn (4 analytes) | multivariate CP exists in statistics | Moderate | High | Rejected: niche, small data |
| 16 | FDR-controlled conformal selection for QC release decisions | Mango | Jin & Candès 2023 (statistics) | Moderate | High | Merged into #1 as decision analysis |
| 17 | Multiview conformal identification | PTIR+Raman | Parham et al. 2026 ACS Meas Sci Au | High | Low (data) | Rejected |

## Stress test of the selected direction (skeptical Talanta editor)

* *Too incremental?* Risk: "applying hierarchical CP to spectra". Mitigation: (i) the paper's first contribution is an
  empirical finding: we quantify how much random-split CP, the classical ASTM-type PLS interval and other common UQ methods
  under-cover under the shifts that dominate NIR practice, across 2 domains, 4 datasets and >100 deployment groups;
  (ii) a chemometrics-specific nonconformity score based on PLS Hotelling T² and Q residuals; (iii) integration with
  standard chemometric model building (group-wise CV) without extra data; (iv) decision-level evaluation (specification-limit compliance).
* *Already solved?* No chemometrics paper found that evaluates conformal validity under season/instrument/region shift.
* *Simpler method achieves the same?* Tested directly: ablations against absolute residuals, random-split CP, classical intervals.
* *Data too small?* No: 85,401 mango spectra; ~40k LUCAS soils.
* *Leakage risk?* High (multiple spectra per fruit; fruit scanned on several instruments; same corn samples on 3 instruments) → fruit/sample-disjoint group splits.
* *Can the improvement vanish under proper statistics?* Unit of analysis = held-out group; paired Wilcoxon tests with Holm correction; cluster bootstrap.
* *Journal fit?* Talanta publishes chemometrics on real analytical data; prediction uncertainty is an analytical figure of merit.
* *Limitation to state honestly:* distribution-free guarantees need ≥ 10 exchangeable calibration groups at 90 % (Lee et al.), so a
  season-level guarantee with 6 training seasons is impossible; this is analysed, not hidden.
