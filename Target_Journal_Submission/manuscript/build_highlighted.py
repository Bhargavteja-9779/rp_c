"""Revised manuscript with the changes since the submitted version highlighted (yellow), as requested by the editor.

usage: python build_highlighted.py revised_content.json out.docx
The submitted version is ../revision_1/submitted_v1_content.json (identical to the content file at git tag submitted-v1).
Rules: every text block of the revision is aligned with its most similar block of the submitted version; inserted or
changed words are highlighted; blocks without a counterpart are highlighted in full. Changed table cells, new table rows,
captions of figures whose image changed, and new references are highlighted. Deleted or moved text is not shown (it is
listed in the response to the reviewers). Author names and affiliations are not marked: the submitted title page already
carried them (the content file of the submission had placeholders that the authors filled in)."""
import copy, difflib, hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
V1 = os.path.join(ROOT, "revision_1", "submitted_v1_content.json")
O, C = "⟦", "⟧"


def toks(t):
    return t.split()


def mark(new, old):
    """Word-level diff: wrap inserted/replaced runs of words of `new` (relative to `old`) in ⟦ ⟧."""
    a, b = toks(old), toks(new)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        seg = b[j1:j2]
        if not seg:
            continue
        out.append(" ".join(seg) if op == "equal" else O + " ".join(seg) + C)
    return " ".join(out)


def best(text, pool):
    """Most similar block of the submitted version (ratio on words)."""
    bt, br = None, 0.0
    w = toks(text)
    for p in pool:
        sm = difflib.SequenceMatcher(None, toks(p), w, autojunk=False)
        if sm.real_quick_ratio() < br or sm.quick_ratio() < br:
            continue
        r = sm.ratio()
        if r > br:
            bt, br = p, r
    return bt, br


def full(t):
    return O + t + C if t.strip() else t


def mark_text(t, pool, thr=0.45):
    if t in pool:
        return t
    old, r = best(t, pool)
    return mark(t, old) if old is not None and r >= thr else full(t)


def fig_changed(path):
    """True if the figure file differs from the one committed at the submitted version."""
    rel = os.path.relpath(path, os.path.dirname(ROOT))
    try:
        old = subprocess.run(["git", "-C", os.path.dirname(ROOT), "show", f"submitted-v1:{rel}"], capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return True
    return hashlib.sha1(old).digest() != hashlib.sha1(open(path, "rb").read()).digest()


def main(new_json, out_docx):
    v1 = json.load(open(V1)); v2 = json.load(open(new_json))
    pool = []
    for b in v1["blocks"]:
        if b["type"] in ("p", "h1", "h2", "h3", "eq"):
            pool.append(b["text"])
        elif b["type"] == "bullets":
            pool += b["items"]
        elif b["type"] in ("fig", "table"):
            pool.append(b["caption"])
            if b.get("note"):
                pool.append(b["note"])
    pool += v1["meta"]["abstract"]
    v1_tables = [b for b in v1["blocks"] if b["type"] == "table"]
    out = copy.deepcopy(v2)
    n_new = 0
    for b in out["blocks"]:
        t = b["type"]
        if t in ("p", "h1", "h2", "h3", "eq"):
            b["text"] = mark_text(b["text"], pool, 0.6 if t.startswith("h") else 0.45)
        elif t == "bullets":
            b["items"] = [mark_text(x, pool) for x in b["items"]]
        elif t == "fig":
            cap = mark_text(b["caption"], pool)
            if fig_changed(b["path"]) and O not in cap[:12]:
                lab = re.match(r"(Fig\. \d+\.)", cap)
                if lab:
                    cap = O + lab.group(1) + " (revised figure)" + C + cap[len(lab.group(1)):]
            b["caption"] = cap
        elif t == "table":
            old, r = best(b["caption"], [x["caption"] for x in v1_tables])
            ot = next((x for x in v1_tables if x["caption"] == old), None) if r >= 0.5 else None
            b["caption"] = mark_text(b["caption"], pool)
            if b.get("note"):
                b["note"] = mark_text(b["note"], pool)
            if ot is None:
                b["rows"] = [[full(str(c)) for c in row] for row in b["rows"]]
                continue
            old_rows = {str(r_[0]): r_ for r_ in ot["rows"]}
            for i, row in enumerate(b["rows"]):
                o = old_rows.get(str(row[0]))
                if o is None:
                    b["rows"][i] = [full(str(c)) for c in row]
                else:
                    b["rows"][i] = [str(c) if j < len(o) and str(c) == str(o[j]) else full(str(c)) for j, c in enumerate(row)]
    out["meta"]["abstract"] = [mark_text(a, v1["meta"]["abstract"], 0.3) for a in out["meta"]["abstract"]]
    strip = lambda r: re.sub(r"^\[\d+\]\s*", "", r)
    old_refs = {strip(r) for r in v1["references"]}
    out["references"] = [r if strip(r) in old_refs else full(r) for r in out["references"]]
    js = out_docx.replace(".docx", "_content.json")
    json.dump(out, open(js, "w"), indent=1, ensure_ascii=False)
    subprocess.run(["node", os.path.join(HERE, "render_docx.js"), js, out_docx], check=True)
    txt = json.dumps(out, ensure_ascii=False)
    print(f"highlighted segments: {txt.count(O)}; written {out_docx}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
