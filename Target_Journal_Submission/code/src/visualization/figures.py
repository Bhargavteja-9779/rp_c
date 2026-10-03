"""Publication figures. Every figure is drawn from machine-generated result files in ``results/``.

Colour assignment is fixed per method (the entity), never by rank, using the validated
categorical palette order of the project's data-visualisation guidelines.
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INK = "#0b0b0b"; INK2 = "#52514e"; GRID = "#e4e3df"; NEUTRAL = "#8a8984"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
METHOD_COLOR = {"GC-D": SLOTS[0], "SCP": SLOTS[1], "ASTM-R": SLOTS[2], "CV+": SLOTS[3], "WCP": SLOTS[4],
                "CQR": SLOTS[5], "G-W-A": SLOTS[6], "ASTM-G": SLOTS[7], "ORACLE": INK2}
METHOD_LABEL = {
    "GC-D": "GC-D (proposed)", "SCP": "Split CP (random)", "ASTM-R": "Classical PLS PI", "ASTM-G": "Classical PI, group-CV RMSE",
    "CV+": "CV+ (random)", "WCP": "Weighted CP", "CQR": "CQR", "G-W-A": "Group CP, abs. score", "ORACLE": "Oracle (target labels)",
    "GPR": "GPR", "BAG": "Bagged PLS", "QGB": "Quantile GBM", "NCP-kNN": "Normalised CP (kNN)",
    "R-U-A": "R-U-A", "R-U-D": "R-U-D", "G-U-A": "G-U-A", "G-U-D": "G-U-D", "GC-D+": "GC-D + finite corr.",
    "HJ+": "Hier. jackknife+", "HJ+-D": "Hier. jackknife+ (D)", "HCP-D": "Hier. split CP (D)", "HCP-A": "Hier. split CP",
}


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "axes.edgecolor": INK2,
        "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
        "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
        "axes.axisbelow": True, "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
        "lines.linewidth": 2.0, "legend.frameon": False})


def save(fig, out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out_dir, f"{name}.{ext}"))
    plt.close(fig)


def color(m):
    return METHOD_COLOR.get(m, NEUTRAL)
