# Internal novelty map (Phase 4)

| Existing work | Contribution | What it does not address |
|---|---|---|
| Faber & Kowalski 1997; Denham 1997; Zhang & Garcia-Munoz 2009 (CILS); ASTM E1655 | Parametric / linearisation PLS prediction intervals | Rely on Gaussian/i.i.d. assumptions; no coverage guarantee; not designed for shift |
| Lin et al. 2022, J. Chemometrics (10.1002/cem.3457) | jackknife+ for PLS, molecular descriptor data | Exchangeable (random) splits only |
| Jović 2025, Food Chemistry 492:145387 | Normalised inductive CP on MIR adulteration data | Random splits; no deployment shift |
| Wiens, Solomatova, Shokatian 2026, Anal. Chem. 98:309 | Conformalised UQ (ensembles, BNN, QR…) for Raman SOC | No group/season/instrument shift analysis |
| Cui et al. 2026 (SSRN preprint 10.2139/ssrn.7528488) | Aggregated inductive CP for NIR | Full text inaccessible to us; title indicates exchangeable aggregation, not group shift |
| Tibshirani et al. 2019 (NeurIPS) | Weighted CP under covariate shift (density ratio) | Needs density ratio in high-dimensional spectra; implemented here as a baseline |
| Dunn, Wasserman, Ramdas 2022 (JASA) | CP for new groups (CDF pooling, subsampling) | No regression with spectral covariates; no chemometrics |
| Lee, Barber, Willett 2026 (ACM JDS) | Hierarchical split CP and hierarchical jackknife+ | Generic absolute-residual scores; no application to analytical calibration |
| Anderson et al. 2020/2021 (Postharvest Biol. Technol.) | Robustness of mango DM models across seasons (RMSEP/bias) | No prediction intervals or coverage |
| Mallick et al. 2026 (arXiv 2608.15500) | Hierarchical CP using initial test-group labels | Survey data; requires labelled target samples |
| Conformal Calibration Transfer, ICML 2026 (arXiv 2609.10737) | Transported CP with paired source/target data | Image classification; requires paired samples |

**Proposed work — genuinely different elements**
1. Formulation of NIR deployment (new season / instrument / region) as a *hierarchical exchangeability* problem and a
   multi-dataset demonstration of the coverage failure of current practice.
2. A PLS-diagnostic (T², Q) normalised nonconformity score fitted on out-of-group residuals, giving sample-specific interval
   widths that grow with spectral extrapolation.
3. A practical cross-fitted group-conformal pipeline built on the group-wise CV that chemometricians already run, plus an exact
   split variant when ≥ 10 calibration groups exist.
4. Evaluation of decision consequences (false compliance against a specification limit).
