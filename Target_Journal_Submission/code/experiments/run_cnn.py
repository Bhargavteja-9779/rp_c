"""E4b: is the group-conformal calibration model-agnostic? Repeats the key comparison on the mango
LOSO task with a 1D-CNN point predictor instead of PLS. The difficulty model σ(x) still uses PLS
T²/Q diagnostics (as model-independent spectral-novelty descriptors).

Usage: python experiments/run_cnn.py --seed 0 [--quick]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.conformal.core import DiagnosticScale, diag_features, split_conformal_quantile, weighted_quantile
from src.evaluation.metrics import summarize_group
from src.evaluation.tasks import get_task
from src.models.cnn import CNN1D
from src.models.pls import PLS1
from src.training.crossfit import CrossFit, group_balanced_weights, make_folds
from src.utils import RESULTS, get_logger, set_seed

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=0)
p.add_argument("--task", default="mango_season_loso")
p.add_argument("--quick", action="store_true")
a = p.parse_args()
set_seed(a.seed)
log = get_logger(f"cnn_{a.task}_seed{a.seed}")
task = get_task(a.task, seed=a.seed)
X, ds = task["X"], task["ds"]
y = ds.y.astype(float); units = ds.meta.unit.to_numpy()
epochs = 5 if a.quick else 40
folds = task["folds"][:1] if a.quick else task["folds"]
rows, pts = [], []
out = os.path.join(RESULTS, "cnn"); os.makedirs(out, exist_ok=True)
for f in folds:
    t0 = time.time()
    tr, te = f["train"], f["test"]
    g = f["calib_group"][tr]
    mk = lambda: CNN1D(epochs=epochs, seed=a.seed, threads=int(os.environ.get("TORCH_THREADS", "2")))
    final = mk().fit(X[tr], y[tr], units[tr]); yhat = final.predict(X[te])
    # PLS diagnostics (model-independent spectral novelty descriptors)
    gfolds = make_folds(g, units[tr], "group")
    pcf = CrossFit(X[tr], y[tr], gfolds, 20)
    A, _ = pcf.choose_A(group_balanced_weights(g))
    pls = PLS1(20).fit(X[tr], y[tr]).set_n_lv(A)
    Qref = np.median(pls.diagnostics(X[tr])["Q"])
    dte = pls.diagnostics(X[te])
    T2g, Qg = pcf.oof_diagnostics(A)
    # out-of-group CNN residuals
    oof_g = np.full(len(tr), np.nan)
    for (itr, ite) in gfolds:
        oof_g[ite] = mk().fit(X[tr][itr], y[tr][itr], units[tr][itr]).predict(X[tr][ite])
    rg = y[tr] - oof_g
    # random unit-grouped 5-fold CNN residuals
    rfolds = make_folds(g, units[tr], "random", n_folds=5, seed=a.seed)
    oof_r = np.full(len(tr), np.nan)
    for (itr, ite) in rfolds:
        oof_r[ite] = mk().fit(X[tr][itr], y[tr][itr], units[tr][itr]).predict(X[tr][ite])
    rr = y[tr] - oof_r
    # random split CP
    rng = np.random.default_rng(a.seed + 1000)
    uu = np.unique(units[tr]); cu = rng.choice(uu, size=int(0.25 * len(uu)), replace=False)
    cal = np.isin(units[tr], cu)
    sm_ = mk().fit(X[tr][~cal], y[tr][~cal], units[tr][~cal])
    q_scp = split_conformal_quantile(np.abs(y[tr][cal] - sm_.predict(X[tr][cal])), 0.1)
    yh_scp = sm_.predict(X[te])
    w = group_balanced_weights(g)
    sigm = DiagnosticScale().fit(diag_features(T2g, Qg, Qref), np.abs(rg))
    sig_cal = sigm.predict(diag_features(T2g, Qg, Qref)); sig_te = sigm.predict(diag_features(dte["T2"], dte["Q"], Qref))
    res = {"CNN-SCP": (yh_scp - q_scp, yh_scp + q_scp)}
    q = weighted_quantile(np.abs(rr), np.ones(len(rr)) / len(rr), 0.9); res["CNN-R-U-A"] = (yhat - q, yhat + q)
    q = weighted_quantile(np.abs(rg), w, 0.9); res["CNN-G-W-A"] = (yhat - q, yhat + q)
    q = weighted_quantile(np.abs(rg) / sig_cal, w, 0.9); res["CNN-GC-D"] = (yhat - q * sig_te, yhat + q * sig_te)
    for meth, (lo, hi) in res.items():
        r = summarize_group(y[te], yhat if meth != "CNN-SCP" else yh_scp, lo, hi, 0.1)
        rows.append(dict(task=a.task, fold=f["name"], group=f["name"].replace("season", ""), method=meth, alpha=0.1,
                         seed=a.seed, **r))
    log.info(f"{f['name']}: rmse={np.sqrt(np.mean((yhat-y[te])**2)):.3f} " +
             " ".join(f"{r['method']}:{r['coverage']:.3f}/{r['width_mean']:.2f}" for r in rows[-4:]) +
             f" ({time.time()-t0:.0f}s)")
pd.DataFrame(rows).to_csv(os.path.join(out, f"groups_cnn_{a.task}_seed{a.seed}.csv"), index=False)
