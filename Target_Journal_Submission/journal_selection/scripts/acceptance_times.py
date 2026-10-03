"""Measure empirical submission-to-acceptance times from publisher-deposited
metadata (PubMed history dates or Crossref 'assertion' fields).

Unit of analysis: individual research article with both a 'received' and an
'accepted' date. Window: articles published in 2025-2026.
Outputs median, IQR and share of articles accepted within 30/60/72 days.
"""
import json, re, statistics, sys, time, urllib.request, urllib.parse
from datetime import date, datetime

UA = {"User-Agent": "journal-timeline-audit/1.0 (mailto:research@example.org)"}

def get(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            time.sleep(2 ** (i + 1))
    raise RuntimeError(url)

def pubmed_times(ta, n=300):
    term = f'"{ta}"[ta] AND ("2025/06/01"[dp] : "2026/12/31"[dp]) AND journal article[pt] NOT review[pt]'
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": n, "retmode": "json", "sort": "pub_date"})
    ids = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + q))["esearchresult"]["idlist"]
    out = []
    for k in range(0, len(ids), 100):
        xml = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(ids[k:k+100]))
        for art in xml.split("<PubmedArticle>")[1:]:
            d = {}
            for st in ("received", "accepted"):
                m = re.search(rf'PubStatus="{st}"><Year>(\d+)</Year><Month>(\d+)</Month><Day>(\d+)</Day>', art)
                if m:
                    d[st] = date(*map(int, m.groups()))
            if len(d) == 2 and d["accepted"] >= d["received"]:
                out.append((d["accepted"] - d["received"]).days)
        time.sleep(0.4)
    return out

def parse_dt(s):
    for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d", "%B %d, %Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except Exception:
            pass
    return None

def crossref_times(issn, n=600):
    out, cursor = [], "*"
    while len(out) < n:
        q = urllib.parse.urlencode({"filter": "from-pub-date:2025-06-01,type:journal-article", "rows": 200, "cursor": cursor, "select": "DOI,assertion"})
        js = json.loads(get(f"https://api.crossref.org/journals/{issn}/works?" + q))["message"]
        items = js["items"]
        if not items:
            break
        for it in items:
            a = {x.get("name", "").lower(): x.get("value", "") for x in it.get("assertion", [])}
            rec = a.get("received") or a.get("received_date")
            acc = a.get("accepted") or a.get("accepted_date")
            if rec and acc:
                r, c = parse_dt(rec), parse_dt(acc)
                if r and c and c >= r:
                    out.append((c - r).days)
        cursor = js.get("next-cursor")
        if not cursor or len(items) < 200:
            break
    return out

def summarize(x):
    if not x:
        return {"n": 0}
    x = sorted(x)
    q = statistics.quantiles(x, n=4)
    return {"n": len(x), "median": statistics.median(x), "q1": q[0], "q3": q[2], "mean": round(statistics.mean(x), 1),
            "pct_le_30": round(100 * sum(v <= 30 for v in x) / len(x), 1),
            "pct_le_60": round(100 * sum(v <= 60 for v in x) / len(x), 1),
            "pct_le_72": round(100 * sum(v <= 72 for v in x) / len(x), 1)}

PUBMED = {
    "Briefings in Bioinformatics (OUP)": "Brief Bioinform",
    "Bioinformatics (OUP)": "Bioinformatics",
    "GigaScience (OUP)": "Gigascience",
    "JAMIA (OUP)": "J Am Med Inform Assoc",
    "NAR Genomics and Bioinformatics (OUP)": "NAR Genom Bioinform",
    "Computers in Biology and Medicine (Elsevier)": "Comput Biol Med",
    "Artificial Intelligence in Medicine (Elsevier)": "Artif Intell Med",
    "Journal of Biomedical Informatics (Elsevier)": "J Biomed Inform",
    "Comput Methods Programs Biomed (Elsevier)": "Comput Methods Programs Biomed",
    "Comput Struct Biotechnol J (Elsevier)": "Comput Struct Biotechnol J",
    "Journal of Cheminformatics (Springer Nature)": "J Cheminform",
    "IEEE J Biomed Health Inform (IEEE)": "IEEE J Biomed Health Inform",
    "Neural Networks (Elsevier)": "Neural Netw",
    "Medical Image Analysis (Elsevier)": "Med Image Anal",
    "npj Digital Medicine (Springer Nature)": "NPJ Digit Med",
    "Patterns (Cell Press)": "Patterns (N Y)",
}
CROSSREF = {
    "Expert Systems with Applications (Elsevier)": "0957-4174",
    "Knowledge-Based Systems (Elsevier)": "0950-7051",
    "Pattern Recognition (Elsevier)": "0031-3203",
    "Engineering Applications of AI (Elsevier)": "0952-1976",
    "Information Sciences (Elsevier)": "0020-0255",
    "Applied Soft Computing (Elsevier)": "1568-4946",
    "Neurocomputing (Elsevier)": "0925-2312",
    "Information Fusion (Elsevier)": "1566-2535",
    "Journal of Big Data (Springer Nature)": "2196-1115",
    "Complex & Intelligent Systems (Springer Nature)": "2199-4536",
    "Energy and AI (Elsevier)": "2666-5468",
}

if __name__ == "__main__":
    res = {}
    for name, ta in PUBMED.items():
        try:
            res[name] = {"source": "PubMed history (received->accepted)", **summarize(pubmed_times(ta))}
        except Exception as e:
            res[name] = {"error": str(e)}
        print(name, res[name], flush=True)
    for name, issn in CROSSREF.items():
        try:
            res[name] = {"source": "Crossref assertion (received->accepted)", **summarize(crossref_times(issn))}
        except Exception as e:
            res[name] = {"error": str(e)}
        print(name, res[name], flush=True)
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "acceptance_times.json", "w"), indent=2)
