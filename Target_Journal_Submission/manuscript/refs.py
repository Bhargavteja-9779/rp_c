"""Reference database. Every entry was checked against Crossref (DOI), arXiv, or the publisher /
journal page (see references_verified.json and supplementary/citation_audit.md).
Style: Elsevier numbered (Talanta): Authors, Title, Journal Volume (Year) pages. https://doi.org/..."""

# Formatted entries (author lists abbreviated to "et al." after six authors, per common Elsevier practice).
REFS = {
 "walsh2020": "K.B. Walsh, J. Blasco, M. Zude-Sasse, X. Sun, Visible-NIR ‘point’ spectroscopy in postharvest fruit and vegetable assessment: the science behind three decades of commercial use, Postharvest Biol. Technol. 168 (2020) 111246. https://doi.org/10.1016/j.postharvbio.2020.111246",
 "gum2008": "JCGM 100:2008, Evaluation of measurement data — Guide to the expression of uncertainty in measurement, Joint Committee for Guides in Metrology (BIPM, IEC, IFCC, ILAC, ISO, IUPAC, IUPAP, OIML), 2008. https://doi.org/10.59161/JCGM100-2008E",
 "wold2001": "S. Wold, M. Sjöström, L. Eriksson, PLS-regression: a basic tool of chemometrics, Chemom. Intell. Lab. Syst. 58 (2001) 109–130. https://doi.org/10.1016/S0169-7439(01)00155-1",
 "astm1655": "ASTM International, ASTM E1655-17, Standard Practices for Infrared Multivariate Quantitative Analysis, West Conshohocken, PA. https://doi.org/10.1520/E1655-17",
 "faber1997": "K. Faber, B.R. Kowalski, Propagation of measurement errors for the validation of predictions obtained by principal component regression and partial least squares, J. Chemom. 11 (1997) 181–238. https://doi.org/10.1002/(SICI)1099-128X(199705)11:3<181::AID-CEM459>3.0.CO;2-7",
 "denham1997": "M.C. Denham, Prediction intervals in partial least squares, J. Chemom. 11 (1997) 39–52. https://doi.org/10.1002/(SICI)1099-128X(199701)11:1<39::AID-CEM433>3.0.CO;2-S",
 "fernandez2003": "J.A. Fernández Pierna, L. Jin, F. Wahl, N.M. Faber, D.L. Massart, Estimation of partial least squares regression prediction uncertainty when the reference values carry a sizeable measurement error, Chemom. Intell. Lab. Syst. 65 (2003) 281–291. https://doi.org/10.1016/S0169-7439(02)00139-9",
 "zhang2009": "L. Zhang, S. Garcia-Munoz, A comparison of different methods to estimate prediction uncertainty using partial least squares (PLS): a practitioner's perspective, Chemom. Intell. Lab. Syst. 97 (2009) 152–158. https://doi.org/10.1016/j.chemolab.2009.03.007",
 "romera2010": "R. Romera, Prediction intervals in partial least squares regression via a new local linearization approach, Chemom. Intell. Lab. Syst. 103 (2010) 122–128. https://doi.org/10.1016/j.chemolab.2010.06.007",
 "vovk2005": "V. Vovk, A. Gammerman, G. Shafer, Algorithmic Learning in a Random World, Springer, New York, 2005. https://doi.org/10.1007/b106715",
 "lei2018": "J. Lei, M. G’Sell, A. Rinaldo, R.J. Tibshirani, L. Wasserman, Distribution-free predictive inference for regression, J. Am. Stat. Assoc. 113 (2018) 1094–1111. https://doi.org/10.1080/01621459.2017.1307116",
 "angelopoulos2023": "A.N. Angelopoulos, S. Bates, Conformal prediction: a gentle introduction, Found. Trends Mach. Learn. 16 (2023) 494–591. https://doi.org/10.1561/2200000101",
 "norinder2014": "U. Norinder, L. Carlsson, S. Boyer, M. Eklund, Introducing conformal prediction in predictive modeling. A transparent and flexible alternative to applicability domain determination, J. Chem. Inf. Model. 54 (2014) 1596–1603. https://doi.org/10.1021/ci5001168",
 "lin2022": "Y. Lin, C. Xu, Z. Zhou, L. Shen, S. Huang, Distribution-free predictive inference for partial least squares regression with applications to molecular descriptors datasets, J. Chemom. 36 (2022) e3457. https://doi.org/10.1002/cem.3457",
 "jovic2025": "O. Jovic, Conformal predictors in chemometric study of mid-infrared food adulteration: quantification of prediction uncertainty, Food Chem. 492 (2025) 145387. https://doi.org/10.1016/j.foodchem.2025.145387",
 "wiens2026": "J.K. Wiens, N. Solomatova, S. Shokatian, Calibrated uncertainty estimation for soil organic carbon from Raman spectra, Anal. Chem. 98 (2026) 309–316. https://doi.org/10.1021/acs.analchem.5c04616",
 "cui2026ssrn": "H. Cui, Y. Qiao, C. Sun, Aggregated inductive conformal prediction for distribution-free uncertainty quantification in near-infrared spectroscopy, SSRN preprint (2026). https://doi.org/10.2139/ssrn.7528488",
 "parham2026": "R.L. Parham, E. Ochoa Rivera, A.M. Ayala, M.E. Clough, Y. Patel, A.J. McNeil, A. Tewari, A.P. Ault, Improved microplastic identification from simultaneously collected photothermal infrared and Raman spectra using multiview conformal prediction, ACS Meas. Sci. Au 6 (2026) 690–702. https://doi.org/10.1021/acsmeasuresciau.6c00002",
 "feudale2002": "R.N. Feudale, N.A. Woody, H. Tan, A.J. Myles, S.D. Brown, J. Ferré, Transfer of multivariate calibration models: a review, Chemom. Intell. Lab. Syst. 64 (2002) 181–192. https://doi.org/10.1016/S0169-7439(02)00085-0",
 "workman2018": "J.J. Workman, A review of calibration transfer practices and instrument differences in spectroscopy, Appl. Spectrosc. 72 (2018) 340–365. https://doi.org/10.1177/0003702817736064",
 "nikzad2018": "R. Nikzad-Langerodi, W. Zellinger, E. Lughofer, S. Saminger-Platz, Domain-invariant partial-least-squares regression, Anal. Chem. 90 (2018) 6693–6701. https://doi.org/10.1021/acs.analchem.8b00498",
 "mikulasek2023": "B. Mikulasek, V. Fonseca Diaz, D. Gabauer, C. Herwig, R. Nikzad-Langerodi, Partial least squares regression with multiple domains, J. Chemom. 37 (2023) e3477. https://doi.org/10.1002/cem.3477",
 "anderson2020": "N.T. Anderson, K.B. Walsh, P.P. Subedi, C.H. Hayes, Achieving robustness across season, location and cultivar for a NIRS model for intact mango fruit dry matter content, Postharvest Biol. Technol. 168 (2020) 111202. https://doi.org/10.1016/j.postharvbio.2020.111202",
 "anderson2021": "N.T. Anderson, K.B. Walsh, J.R. Flynn, J.P. Walsh, Achieving robustness across season, location and cultivar for a NIRS model for intact mango fruit dry matter content. II. Local PLSR and ANN modelling, Postharvest Biol. Technol. 171 (2021) 111358. https://doi.org/10.1016/j.postharvbio.2020.111358",
 "sun2020": "X. Sun, P. Subedi, K.B. Walsh, Achieving robustness to temperature change of a NIRS-PLSR model for intact mango fruit dry matter content, Postharvest Biol. Technol. 162 (2020) 111117. https://doi.org/10.1016/j.postharvbio.2019.111117",
 "mishra2021": "P. Mishra, D. Passos, A synergistic use of chemometrics and deep learning improved the predictive performance of near-infrared spectroscopy models for dry matter prediction in mango fruit, Chemom. Intell. Lab. Syst. 212 (2021) 104287. https://doi.org/10.1016/j.chemolab.2021.104287",
 "cui2018": "C. Cui, T. Fearn, Modern practical convolutional neural networks for multivariate regression: applications to NIR calibration, Chemom. Intell. Lab. Syst. 182 (2018) 9–20. https://doi.org/10.1016/j.chemolab.2018.07.008",
 "tibshirani2019": "R.J. Tibshirani, R. Foygel Barber, E. Candès, A. Ramdas, Conformal prediction under covariate shift, in: Adv. Neural Inf. Process. Syst. 32 (NeurIPS 2019). arXiv:1904.06019",
 "barber2023": "R.F. Barber, E.J. Candès, A. Ramdas, R.J. Tibshirani, Conformal prediction beyond exchangeability, Ann. Stat. 51 (2023) 816–845. https://doi.org/10.1214/23-AOS2276",
 "gibbs2021": "I. Gibbs, E. Candès, Adaptive conformal inference under distribution shift, in: Adv. Neural Inf. Process. Syst. 34 (NeurIPS 2021). arXiv:2106.00170",
 "fannjiang2022": "C. Fannjiang, S. Bates, A.N. Angelopoulos, J. Listgarten, M.I. Jordan, Conformal prediction under feedback covariate shift for biomolecular design, Proc. Natl. Acad. Sci. U.S.A. 119 (2022) e2204569119. https://doi.org/10.1073/pnas.2204569119",
 "dunn2023": "R. Dunn, L. Wasserman, A. Ramdas, Distribution-free prediction sets for two-layer hierarchical models, J. Am. Stat. Assoc. 118 (2023) 2491–2502. https://doi.org/10.1080/01621459.2022.2060112",
 "lee2026": "Y. Lee, R.F. Barber, R. Willett, Distribution-free inference with hierarchical data, ACM J. Data Sci. (2026) 3786352. https://doi.org/10.1145/3786352 (preprint arXiv:2306.06342)",
 "mallick2026": "S. Mallick, E. Tchetgen Tchetgen, E. Dobriban, Y. Lee, Generalized hierarchical conformal prediction, arXiv:2608.15500 (2026)",
 "cct2026": "A. Doula, Conformal calibration transfer, arXiv:2609.10737 (2026)",
 "barber2021": "R.F. Barber, E.J. Candès, A. Ramdas, R.J. Tibshirani, Predictive inference with the jackknife+, Ann. Stat. 49 (2021) 486–507. https://doi.org/10.1214/20-AOS1965",
 "papadopoulos2011": "H. Papadopoulos, V. Vovk, A. Gammerman, Regression conformal prediction with nearest neighbours, J. Artif. Intell. Res. 40 (2011) 815–840. https://doi.org/10.1613/jair.3198",
 "romano2019": "Y. Romano, E. Patterson, E. Candès, Conformalized quantile regression, in: Adv. Neural Inf. Process. Syst. 32 (NeurIPS 2019). arXiv:1905.03222",
 "jackson1979": "J.E. Jackson, G.S. Mudholkar, Control procedures for residuals associated with principal component analysis, Technometrics 21 (1979) 341–349. https://doi.org/10.1080/00401706.1979.10489779",
 "savitzky1964": "A. Savitzky, M.J.E. Golay, Smoothing and differentiation of data by simplified least squares procedures, Anal. Chem. 36 (1964) 1627–1639. https://doi.org/10.1021/ac60214a047",
 "barnes1989": "R.J. Barnes, M.S. Dhanoa, S.J. Lister, Standard normal variate transformation and de-trending of near-infrared diffuse reflectance spectra, Appl. Spectrosc. 43 (1989) 772–777. https://doi.org/10.1366/0003702894202201",
 "gneiting2007": "T. Gneiting, A.E. Raftery, Strictly proper scoring rules, prediction, and estimation, J. Am. Stat. Assoc. 102 (2007) 359–378. https://doi.org/10.1198/016214506000001437",
 "safanelli2025": "J.L. Safanelli, T. Hengl, L.L. Parente, R. Minarik, D.E. Bloom, K. Todd-Brown, et al., Open Soil Spectral Library (OSSL): building reproducible soil calibration models through open development and community engagement, PLoS One 20 (2025) e0296545. https://doi.org/10.1371/journal.pone.0296545",
 "orgiazzi2018": "A. Orgiazzi, C. Ballabio, P. Panagos, A. Jones, O. Fernández-Ugalde, LUCAS Soil, the largest expandable soil dataset for Europe: a review, Eur. J. Soil Sci. 69 (2018) 140–153. https://doi.org/10.1111/ejss.12499",
 "mango_data": "N. Anderson, Mango DMC and NIR spectra (Version 5), Mendeley Data (2024). https://doi.org/10.17632/46htwnp833.5",
 "corn_data": "Eigenvector Research, Inc., Corn data set (80 samples measured on three NIR spectrometers; data from Cargill). https://eigenvector.com/resources/data-sets/ (accessed 3 October 2026)",
 "tablet_data": "Eigenvector Research, Inc., NIR pharmaceutical tablets ‘Shootout 2002’ data set. https://eigenvector.com/resources/data-sets/ (accessed 3 October 2026)",
 "roberts2017": "D.R. Roberts, V. Bahn, S. Ciuti, M.S. Boyce, J. Elith, G. Guillera-Arroita, et al., Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure, Ecography 40 (2017) 913–929. https://doi.org/10.1111/ecog.02881",
 "wilcoxon1945": "F. Wilcoxon, Individual comparisons by ranking methods, Biom. Bull. 1 (1945) 80–83. https://doi.org/10.2307/3001968",
 "holm1979": "S. Holm, A simple sequentially rejective multiple test procedure, Scand. J. Stat. 6 (1979) 65–70.",
 "kerby2014": "D.S. Kerby, The simple difference formula: an approach to teaching nonparametric correlation, Compr. Psychol. 3 (2014) 11.IT.3.1. https://doi.org/10.2466/11.IT.3.1",
 "breiman1996": "L. Breiman, Bagging predictors, Mach. Learn. 24 (1996) 123–140. https://doi.org/10.1007/BF00058655",
 "rasmussen2006": "C.E. Rasmussen, C.K.I. Williams, Gaussian Processes for Machine Learning, MIT Press, Cambridge, MA, 2006. https://doi.org/10.7551/mitpress/3206.001.0001",
 "ke2017": "G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, et al., LightGBM: a highly efficient gradient boosting decision tree, in: Adv. Neural Inf. Process. Syst. 30 (NIPS 2017).",
 "pedregosa2011": "F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, et al., Scikit-learn: machine learning in Python, J. Mach. Learn. Res. 12 (2011) 2825–2830.",
 "paszke2019": "A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan, et al., PyTorch: an imperative style, high-performance deep learning library, in: Adv. Neural Inf. Process. Syst. 32 (NeurIPS 2019).",
}


class Citer:
    """Numbers references in order of first citation (Elsevier numbered style)."""

    def __init__(self):
        self.order = []

    def __call__(self, *keys):
        nums = []
        for k in keys:
            if k not in REFS:
                raise KeyError(f"unverified/missing reference: {k}")
            if k not in self.order:
                self.order.append(k)
            nums.append(self.order.index(k) + 1)
        nums = sorted(set(nums))
        # compress ranges: [1–3,5]
        parts, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            parts.append(f"{nums[i]}–{nums[j]}" if j - i >= 2 else ",".join(str(n) for n in nums[i:j + 1]))
            i = j + 1
        return "[" + ",".join(parts) + "]"

    def bibliography(self):
        return [f"[{i + 1}] {REFS[k]}" for i, k in enumerate(self.order)]
