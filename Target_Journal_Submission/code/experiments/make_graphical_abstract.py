"""Graphical abstract (Elsevier: landscape, readable at 5 x 13 cm). Data from results/summary_results.csv."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from src.visualization.figures import INK, INK2, SLOTS, style, save, color
from src.utils import RESULTS
style()
s = pd.read_csv(os.path.join(RESULTS, "summary_results.csv")); s = s[s.alpha == 0.1]
tasks = [("mango_season_forward", "Next season"), ("mango_season_loso", "New season"), ("mango_instrument", "New instrument"),
         ("ossl_lucas_block", "New soil region")]
fig = plt.figure(figsize=(13 / 2.54 * 1.6, 5 / 2.54 * 1.6))
ax0 = fig.add_axes([0.0, 0.0, 0.42, 1.0]); ax0.set_axis_off(); ax0.set_xlim(0, 10); ax0.set_ylim(0, 10)
def box(x, y, w, h, t, fc="#f4f4f2", ec=INK2, bold=False, fs=7.5):
    ax0.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=ec, lw=0.8))
    ax0.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=INK, fontweight="bold" if bold else "normal")
box(0.3, 6.6, 4.2, 2.8, "Calibration spectra\nfrom K seasons /\ninstruments / regions")
box(5.3, 6.6, 4.4, 2.8, "Out-of-group PLS\nresiduals  +  T², Q")
box(0.3, 1.0, 9.4, 4.2, "Group-balanced quantile\nŷ(x) ± q̂·σ(T², Q)", fc="#cde2fb", ec=SLOTS[0], bold=True, fs=8.5)
ax0.annotate("", (5.3, 8.0), (4.5, 8.0), arrowprops=dict(arrowstyle="-|>", color=INK2))
ax0.annotate("", (5.0, 5.2), (7.5, 6.6), arrowprops=dict(arrowstyle="-|>", color=INK2))
ax = fig.add_axes([0.55, 0.2, 0.42, 0.62])
y = np.arange(len(tasks))
v1 = [float(s[(s.task == t) & (s.method == "SCP")].coverage.iloc[0]) for t, _ in tasks]
v2 = [float(s[(s.task == t) & (s.method == "GC-D")].coverage.iloc[0]) for t, _ in tasks]
for yy, a, b in zip(y, v1, v2):
    ax.annotate("", (b - 0.004, yy), (a + 0.004, yy), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.9))
ax.plot(v1, y, "o", ms=7, color=color("SCP"), label="Random-split conformal")
ax.plot(v2, y, "o", ms=7, color=color("GC-D"), label="Group-conformal (GC-D)")
for yy, a, b in zip(y, v1, v2):
    ax.text(a, yy - 0.28, f"{a:.2f}", ha="center", fontsize=6.5, color=INK)
    ax.text(b, yy - 0.28, f"{b:.2f}", ha="center", fontsize=6.5, color=INK)
ax.axvline(0.9, color=INK2, ls="--", lw=0.8)
ax.set_yticks(y); ax.set_yticklabels([l for _, l in tasks]); ax.set_xlim(0.74, 0.93); ax.set_ylim(len(tasks) - 0.5, -0.8)
ax.set_xlabel("Coverage of nominal 90 % intervals (dashed: target)")
ax.legend(fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handletextpad=0.3)
ax.grid(axis="y", visible=False)
save(fig, os.path.join(os.path.dirname(RESULTS), "figures"), "graphical_abstract")
