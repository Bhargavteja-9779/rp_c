"""Final consistency audit (Phase 34): checks hard-coded statements in the text against the data/results and the
structural integrity of the generated manuscript. Writes ../REVIEW/final_audit_checks.json and exits non-zero on failure."""
import json, os, re, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(HERE), "code")
sys.path.insert(0, CODE)
from src.data.loaders import load_mango, load_ossl, load_corn, load_tablets

content = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Final_Manuscript_content.json")))
text = " ".join(b.get("text", "") + " " + b.get("caption", "") + " " + " ".join(b.get("items", []))
                for b in content["blocks"]) + " " + " ".join(content["meta"]["abstract"])
checks = []


def check(name, ok, detail=""):
    checks.append(dict(check=name, ok=bool(ok), detail=str(detail)))


mg = load_mango(); m = mg.meta
lu = load_ossl("LUCAS.SSL"); ks = load_ossl("KSSL.SSL")
check("mango spectra 85,401", len(mg) == 85401 and "85,401" in text, len(mg))
check("mango fruit 10,560", m.unit.nunique() == 10560 and "10,560" in text, m.unit.nunique())
check("31 instruments", m.instrument.nunique() == 31, m.instrument.nunique())
check("199 populations", m.population.nunique() == 199, m.population.nunique())
check("ten cultivars", m.cultivar.nunique() == 10, m.cultivar.nunique())
check("seasons 2015-2021", sorted(m.season.unique()) == list(range(2015, 2022)))
multi = (m.groupby("unit").instrument.nunique() > 1).sum()
check("7100 fruit on >1 instrument", multi == 7100 and "7100" in text, multi)
spf = len(mg) / m.unit.nunique()
check("8.1 spectra per fruit", f"{spf:.1f}" == "8.1" and "8.1 spectra per fruit" in text, round(spf, 3))
fr = m.groupby("instrument").unit.nunique()
check("24 instruments with >=300 fruit", (fr >= 300).sum() == 24 and "24 instruments" in text, (fr >= 300).sum())
check("LUCAS 40,175", len(lu) == 40175 and "40,175" in text, len(lu))
check("KSSL 19,747", len(ks) == 19747 and "19,747" in text, len(ks))
check("30 LUCAS blocks", lu.meta.block.nunique() == 30, lu.meta.block.nunique())
tot = len(mg) + len(lu) + len(ks) + 240 + 1310
check("146,873 total spectra", tot == 146873 and "146,873" in text, tot)
tb = load_tablets(); n_tab = tb.meta.unit.nunique()
check("655 tablets (155/40/460)", n_tab == 655 and tb.meta.groupby("partition").unit.nunique().to_dict() == {"calibrate": 155, "test": 460, "validate": 40}, n_tab)
check("80 corn samples x 3 instruments", len(load_corn()) == 240)
pop = m[m.population == "114500"]
check("population 114500 = green Kensington Pride 2020",
      set(pop.cultivar) == {"kp"} and set(pop.physio_stage) == {"green"} and set(pop.season) == {2020} and "114500" in text)
# structure
heads = [b["text"] for b in content["blocks"] if b["type"] == "h2" and b["text"][:2] == "4."]
nums = [int(re.match(r"4\.(\d+)", h).group(1)) for h in heads]
check("section 4 subsections consecutive", nums == list(range(1, len(nums) + 1)), nums)
figs = [b for b in content["blocks"] if b["type"] == "fig"]
fignums = [int(re.match(r"Fig\. (\d+)", f["caption"]).group(1)) for f in figs]
check("figure numbers consecutive", fignums == list(range(1, len(fignums) + 1)), fignums)
cited = sorted(set(int(x) for x in re.findall(r"Fig\. (\d+)", text)))
check("every cited figure exists", all(c in fignums for c in cited), cited)
tabs = [b for b in content["blocks"] if b["type"] == "table"]
tabnums = [int(re.match(r"Table (\d+)", t["caption"]).group(1)) for t in tabs]
check("table numbers consecutive", tabnums == list(range(1, len(tabnums) + 1)), tabnums)
check("every cited table exists", all(int(c) in tabnums for c in re.findall(r"Table (\d+)", text)))
sup = sorted(set(re.findall(r"Supplementary Table (S\d+)", text)))
check("supplementary tables cited within S1-S14", all(1 <= int(x[1:]) <= 14 for x in sup), sup)
check("no nan in text", not re.search(r"\bnan\b", text))
refs = content["references"]
cites = sorted(set(int(n) for grp in re.findall(r"\[([\d,–]+)\]", text) for part in grp.split(",")
                   for n in (range(int(part.split("–")[0]), int(part.split("–")[1]) + 1) if "–" in part else [part])))
check("every citation number has a reference", max(cites) <= len(refs), (max(cites), len(refs)))
check("every reference is cited", set(cites) == set(range(1, len(refs) + 1)))
for p in [f["path"] for f in figs]:
    check(f"figure file exists: {os.path.basename(p)}", os.path.exists(p))
ok = all(c["ok"] for c in checks)
json.dump(dict(all_passed=ok, checks=checks), open(os.path.join(os.path.dirname(HERE), "REVIEW", "final_audit_checks.json"), "w"), indent=1)
for c in checks:
    print(("PASS " if c["ok"] else "FAIL ") + c["check"] + ("" if c["ok"] else f"  [{c['detail']}]"))
sys.exit(0 if ok else 1)
