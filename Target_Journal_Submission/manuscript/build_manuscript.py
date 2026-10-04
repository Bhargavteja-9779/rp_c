"""Assemble the manuscript: static text + results text generated from result files -> JSON -> DOCX.
Every number in the results text is read from code/results/*.json|csv (no manual numbers)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(HERE), "code")
sys.path.insert(0, CODE); sys.path.insert(0, HERE)
from refs import Citer
import text_static as TS

def numbers():
    import numpy as np, pandas as pd
    from src.data.loaders import load_mango, load_ossl
    mg = load_mango(); lu = load_ossl("LUCAS.SSL"); ks = load_ossl("KSSL.SSL")
    fr = mg.meta.groupby("instrument").unit.nunique()
    N = dict(mango_spectra=f"{len(mg):,}", mango_fruit=f"{mg.meta.unit.nunique():,}",
             mango_instruments=mg.meta.instrument.nunique(), mango_pops=mg.meta.population.nunique(),
             mango_inst_tasks=int((fr >= 300).sum()), lucas_n=f"{len(lu):,}", kssl_n=f"{len(ks):,}",
             n_spectra_total=f"{len(mg) + len(lu) + len(ks) + 240 + 1310:,}", n_shift_tasks=12)
    return N

def build(out_docx, results_module=None, extra_flags=()):
    C = Citer(); N = numbers()
    blocks = []
    for sec in (TS.introduction(C, N), TS.theory(C), TS.experimental(C, N)):
        blocks += sec
    meta, tail = None, []
    if results_module:
        R = __import__(results_module)
        res_blocks, meta, tail = R.results(C, N)
        blocks += res_blocks
    blocks += tail
    if meta is None:
        meta = dict(title="DRAFT", authors="[Author names]", affiliations=["[Affiliation]"], corresponding="[Corresponding author]",
                    abstract=["[abstract]"], keywords=["NIR"])
    # automatic numbering of the Section-4 subsections (results-dependent sections may be absent)
    import re
    mapping, k = {}, 0
    for i, b in enumerate(blocks):
        if b[0] == "h2" and re.match(r"4\.\d+\. ", b[1]):
            k += 1
            old = re.match(r"4\.(\d+)\. ", b[1]).group(1)
            mapping[f"4.{old}"] = f"4.{k}"
            blocks[i] = ("h2", re.sub(r"^4\.\d+\. ", f"4.{k}. ", b[1]))
    def remap(t):
        return re.sub(r"Section (4\.\d+)", lambda m_: "Section " + mapping.get(m_.group(1), m_.group(1)), t)
    blocks = [(b[0], remap(b[1]), *b[2:]) if b[0] in ("p", "h1") else
              (b[0], [remap(x) for x in b[1]]) if b[0] == "bullets" else b for b in blocks]
    # typographic minus for negative numbers in running text, captions and table cells (not in references/DOIs)
    MINUS = lambda t: re.sub(r"(?<=[\s(=\[])-(?=\d)", "−", t) if isinstance(t, str) else t
    blocks = [(b[0], MINUS(b[1]), *b[2:]) if b[0] in ("p",) else
              (b[0], [MINUS(x) for x in b[1]]) if b[0] == "bullets" else
              (b[0], [[MINUS(c) if not c.startswith("-") else "−" + c[1:] for c in map(str, r)] for r in b[1]], MINUS(b[2]), *b[3:])
              if b[0] == "table" else b for b in blocks]
    conv = []
    for b in blocks:
        t = b[0]
        if t in ("h1", "h2", "h3", "p"): conv.append(dict(type=t, text=b[1]))
        elif t == "eq": conv.append(dict(type="eq", text=b[1], num=b[2]))
        elif t == "bullets": conv.append(dict(type="bullets", items=b[1]))
        elif t == "fig": conv.append(dict(type="fig", path=b[1], caption=b[2], width_in=b[3] if len(b) > 3 else 6.3))
        elif t == "table": conv.append(dict(type="table", rows=b[1], caption=b[2], note=b[3] if len(b) > 3 else None,
                                            highlight_rows=b[4] if len(b) > 4 else None))
        elif t == "pagebreak": conv.append(dict(type="pagebreak"))
    content = dict(meta=meta, blocks=conv, references=C.bibliography())
    js = out_docx.replace(".docx", "_content.json")
    json.dump(content, open(js, "w"), indent=1, ensure_ascii=False)
    subprocess.run(["node", os.path.join(HERE, "render_docx.js"), js, out_docx, *extra_flags], check=True)
    return content

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "draft_static.docx"),
          sys.argv[2] if len(sys.argv) > 2 else None)
