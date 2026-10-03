"""Results, discussion, conclusions, declarations and front matter — every number is read from
code/results (summary_results.csv, comparisons, hypotheses.json, extra results). Qualitative statements
that depend on the data (direction of an effect, number of tasks) are computed, not hard-coded."""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(HERE), "code")
R = os.path.join(CODE, "results")
FIG = os.path.join(CODE, "figures")
TAB = os.path.join(CODE, "tables")

MAIN = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
        "corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
CORN = MAIN[5:]
NICE = {"mango_season_loso": "mango, new season (LOSO)", "mango_season_forward": "mango, next season (forward)",
        "mango_instrument": "mango, new instrument", "mango_population": "mango, new population",
        "ossl_lucas_block": "soil, new region", "corn_moisture": "corn moisture", "corn_oil": "corn oil",
        "corn_protein": "corn protein", "corn_starch": "corn starch", "ossl_lucas_campaign": "soil, other campaign",
        "ossl_kssl_to_lucas": "soil, KSSL → LUCAS", "tablets": "tablets"}


def load():
    s = pd.read_csv(os.path.join(R, "summary_results.csv"))
    c = pd.read_csv(os.path.join(R, "comparisons_alpha0.1.csv"))
    h = json.load(open(os.path.join(R, "hypotheses.json")))
    m = json.load(open(os.path.join(R, "metrics.json")))
    ex = json.load(open(os.path.join(R, "extra_results.json"))) if os.path.exists(os.path.join(R, "extra_results.json")) else {}
    return s, c, h, m, ex


def f3(x):
    return "∞" if not np.isfinite(x) else f"{x:.3f}"


def f2(x):
    return "∞" if not np.isfinite(x) else f"{x:.2f}"


def pval(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


class S:
    def __init__(self, s):
        self.s = s

    def __call__(self, task, method, field="coverage", alpha=0.1):
        d = self.s[(self.s.task == task) & (self.s.method == method) & (self.s.alpha == alpha)]
        return float(d[field].iloc[0]) if len(d) else float("nan")

    def rng(self, tasks, method, field="coverage", alpha=0.1):
        v = [self(t, method, field, alpha) for t in tasks]
        v = [x for x in v if np.isfinite(x)]
        return min(v), max(v)


def csv_rows(path, keep=None, rename=None):
    d = pd.read_csv(path, dtype=str).fillna("–")
    if keep:
        d = d[keep]
    if rename:
        d = d.rename(columns=rename)
    return [list(d.columns)] + d.values.tolist()
