"""Fetch authoritative metadata for every cited DOI from Crossref and arXiv; write references_verified.json."""
import json, time, urllib.request, urllib.parse, re
DOIS = {
 "lei2018": "10.1080/01621459.2017.1307116", "barber2021": "10.1214/20-aos1965", "barber2023": "10.1214/23-aos2276",
 "papadopoulos2011": "10.1613/jair.3198", "vovk2005": "10.1007/b106715", "dunn2023": "10.1080/01621459.2022.2060112",
 "lee2026": "10.1145/3786352", "lin2022": "10.1002/cem.3457", "wiens2026": "10.1021/acs.analchem.5c04616",
 "anderson2020": "10.1016/j.postharvbio.2020.111202", "anderson2021": "10.1016/j.postharvbio.2020.111358",
 "nikzad2018": "10.1021/acs.analchem.8b00498", "zhang2009": "10.1016/j.chemolab.2009.03.007",
 "astm1655": "10.1520/e1655-17", "wold2001": "10.1016/S0169-7439(01)00155-1", "savitzky1964": "10.1021/ac60214a047",
 "barnes1989": "10.1366/0003702894202201", "gneiting2007": "10.1198/016214506000001437",
 "safanelli2025": "10.1371/journal.pone.0296545", "orgiazzi2018": "10.1111/ejss.12499",
 "feudale2002": "10.1016/S0169-7439(02)00085-0", "roberts2017": "10.1111/ecog.02881", "kerby2014": "10.2466/11.IT.3.1",
 "angelopoulos2023": "10.1561/2200000101", "norinder2014": "10.1021/ci5001168", "cui2018": "10.1016/j.chemolab.2018.07.008",
 "walsh2020": "10.1016/j.postharvbio.2020.111246", "jackson1979": "10.1080/00401706.1979.10489779",
 "breiman1996": "10.1007/BF00058655", "denham1997": "10.1002/(sici)1099-128x(199701)11:1<39::aid-cem433>3.0.co;2-s",
 "fernandez2003": "10.1016/s0169-7439(02)00139-9", "romera2010": "10.1016/j.chemolab.2010.06.007",
 "fannjiang2022": "10.1073/pnas.2204569119", "yang2024": "10.1093/jrsssb/qkae009",
 "mikulasek2023": "10.1002/cem.3477", "sun2020": "10.1016/j.postharvbio.2019.111117",
 "pedregosa2011": None,
}
ARXIV = {"tibshirani2019": "1904.06019", "romano2019": "1905.03222", "gibbs2021": "2106.00170",
         "mallick2026": "2608.15500", "cct2026": "2609.10737", "lee2023arxiv": "2306.06342"}
SEARCH = {"jovic2025": "Conformal predictors in chemometric study of mid-infrared food adulteration quantification of prediction uncertainty",
          "mishra2021": "A synergistic use of chemometrics and deep learning improved the predictive performance of near-infrared spectroscopy models for dry matter prediction in mango fruit",
          "faber1997": "Propagation of measurement errors for the validation of predictions obtained by principal component regression and partial least squares",
          "holm1979": "A simple sequentially rejective multiple test procedure",
          "wilcoxon1945": "Individual comparisons by ranking methods",
          "ke2017": "LightGBM: A Highly Efficient Gradient Boosting Decision Tree",
          "paszke2019": "PyTorch: An Imperative Style, High-Performance Deep Learning Library",
          "pedregosa2011": "Scikit-learn: Machine Learning in Python",
          "cui2026ssrn": "Aggregated Inductive Conformal Prediction for Distribution-Free Uncertainty Quantification in Near-Infrared Spectroscopy",
          "parham2026": "Improved Microplastic Identification from Simultaneously Collected Photothermal Infrared and Raman Spectra Using Multiview Conformal Prediction",
          "workman2018": "A Review of Calibration Transfer Practices and Instrument Differences in Spectroscopy",
          "rasmussen2006": "Gaussian Processes for Machine Learning Rasmussen Williams"}
H = {"User-Agent": "refcheck/1.0 (mailto:research@example.org)"}
def get(u):
    for i in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60).read().decode()
        except Exception as e:
            time.sleep(2 ** i); err = e
    raise err
def cr_item(m):
    return dict(doi=m.get("DOI"), title=(m.get("title") or [""])[0], journal=(m.get("container-title") or [""])[0],
                year=(m.get("issued", {}).get("date-parts") or [[None]])[0][0], volume=m.get("volume"), issue=m.get("issue"),
                pages=m.get("page") or m.get("article-number"), publisher=m.get("publisher"), type=m.get("type"),
                authors=[(a.get("family") or a.get("name") or "") + (", " + a["given"] if a.get("given") else "") for a in m.get("author", [])])
out = {}
for k, d in DOIS.items():
    if not d: continue
    try:
        out[k] = {"source": "crossref-doi", **cr_item(json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(d)))["message"])}
    except Exception as e:
        out[k] = {"source": "crossref-doi", "doi": d, "error": str(e)}
    time.sleep(0.3)
for k, q in SEARCH.items():
    js = json.loads(get("https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": q, "rows": 3})))["message"]["items"]
    out[k] = {"source": "crossref-search", "query": q, "candidates": [cr_item(m) for m in js]}
    time.sleep(0.3)
for k, a in ARXIV.items():
    x = get(f"http://export.arxiv.org/api/query?id_list={a}")
    t = re.search(r"<entry>.*?<title>(.*?)</title>", x, re.S); au = re.findall(r"<name>(.*?)</name>", x)
    pub = re.search(r"<entry>.*?<published>(\d{4})", x, re.S)
    out[k] = {"source": "arxiv", "arxiv": a, "title": " ".join(t.group(1).split()) if t else None, "authors": au,
              "year": int(pub.group(1)) if pub else None}
    time.sleep(3)
json.dump(out, open("references_verified.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items():
    if v["source"] == "crossref-search":
        c = v["candidates"][0]; print(f"{k}: SEARCH-> {c['year']} | {c['title'][:90]} | {c['journal'][:40]} | {c['doi']}")
    else:
        print(f"{k}: {v.get('year')} | {str(v.get('title'))[:90]} | {str(v.get('journal',''))[:40]} | {v.get('error','')}")
