"""Per-spectrum (row-wise) preprocessing. None of these transforms has parameters estimated
from other samples, so they cannot leak information between training and test data."""
import numpy as np
from scipy.signal import savgol_filter


def snv(X):
    X = np.asarray(X, float)
    return (X - X.mean(1, keepdims=True)) / (X.std(1, keepdims=True) + 1e-12)


def savgol(X, window=13, poly=2, deriv=2):
    return savgol_filter(np.asarray(X, float), window_length=window, polyorder=poly, deriv=deriv, axis=1)


def preprocess(X, recipe):
    """Apply a recipe, e.g. [("savgol", {"window": 13, "deriv": 2}), ("snv", {})]."""
    out = np.asarray(X, float)
    for name, kw in recipe:
        if name == "snv":
            out = snv(out)
        elif name == "savgol":
            out = savgol(out, **kw)
        elif name == "none":
            pass
        else:
            raise ValueError(name)
    return out
