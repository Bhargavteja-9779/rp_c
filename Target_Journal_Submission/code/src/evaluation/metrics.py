"""Interval evaluation metrics."""
import numpy as np


def interval_score(y, lo, hi, alpha):
    """Winkler / interval score (Gneiting & Raftery 2007): proper score for central (1−α) intervals."""
    lo = np.asarray(lo, float); hi = np.asarray(hi, float); y = np.asarray(y, float)
    return (hi - lo) + (2 / alpha) * np.clip(lo - y, 0, None) + (2 / alpha) * np.clip(y - hi, 0, None)


def point_metrics(y, lo, hi, alpha):
    cov = (y >= lo) & (y <= hi)
    width = hi - lo
    return cov, width, interval_score(y, lo, hi, alpha)


def summarize_group(y, yhat, lo, hi, alpha):
    cov, width, isc = point_metrics(y, lo, hi, alpha)
    fin = np.isfinite(width)
    return {
        "n": int(len(y)),
        "coverage": float(cov.mean()),
        "width_mean": float(np.mean(width)) if fin.all() else float("inf"),
        "width_median": float(np.median(width)),
        "interval_score": float(np.mean(isc)) if fin.all() else float("inf"),
        "finite_frac": float(fin.mean()),
        "rmse": float(np.sqrt(np.mean((y - yhat) ** 2))),
        "bias": float(np.mean(yhat - y)),
        "sep": float(np.std(yhat - y, ddof=1)) if len(y) > 1 else float("nan"),
    }
