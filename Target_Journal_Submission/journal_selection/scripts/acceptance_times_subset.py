"""Acceptance times restricted to chemometrics / machine-learning papers."""
import json, sys, time, re, urllib.parse
from datetime import date
sys.path.insert(0, "scripts")
from acceptance_times import get, summarize
def subset(ta, topic, n=300):
    term = f'"{ta}"[ta] AND ("2024/06/01"[dp] : "2026/12/31"[dp]) AND ({topic}) NOT review[pt]'
    q = urllib.parse.urlencode({"db":"pubmed","term":term,"retmax":n,"retmode":"json","sort":"pub_date"})
    ids = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"+q))["esearchresult"]["idlist"]
    out, titles = [], []
    for k in range(0, len(ids), 100):
        xml = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="+",".join(ids[k:k+100]))
        for art in xml.split("<PubmedArticle>")[1:]:
            d = {}
            for st in ("received","accepted"):
                m = re.search(rf'PubStatus="{st}"><Year>(\d+)</Year><Month>(\d+)</Month><Day>(\d+)</Day>', art)
                if m: d[st] = date(*map(int, m.groups()))
            t = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", art, re.S)
            if len(d)==2 and d["accepted"]>=d["received"]:
                out.append((d["accepted"]-d["received"]).days); titles.append(t.group(1) if t else "")
        time.sleep(0.4)
    return out, titles
topic = 'chemometric*[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab] OR "partial least squares"[tiab] OR "neural network"[tiab] OR "calibration transfer"[tiab] OR "multivariate calibration"[tiab]'
res = {}
for name, ta in {"Talanta":"Talanta","Analytica Chimica Acta":"Anal Chim Acta","Spectrochim Acta A":"Spectrochim Acta A Mol Biomol Spectrosc","Food Chemistry":"Food Chem"}.items():
    x, t = subset(ta, topic)
    res[name] = {"subset":"chemometrics/ML papers 2024-06..2026", **summarize(x), "example_titles": t[:25]}
    print(name, {k:v for k,v in res[name].items() if k!="example_titles"}, flush=True)
json.dump(res, open("acceptance_times_chemometrics_subset.json","w"), indent=2)
