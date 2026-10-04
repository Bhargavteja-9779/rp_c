"""Generate all manuscript figures from result files (no manual numbers)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from src.visualization.figures import (GRID, INK, INK2, METHOD_LABEL, NEUTRAL, SLOTS, color, save, style)
from src.utils import RESULTS

ROOT = os.path.dirname(RESULTS)
FIG = os.environ.get("FIG_DIR", os.path.join(ROOT, "figures"))
TASK_SHORT = {"mango_season_loso": "Mango: new season", "mango_season_forward": "Mango: next season",
              "mango_instrument": "Mango: new instrument", "mango_population": "Mango: new population",
              "ossl_lucas_block": "Soil: new region", "ossl_lucas_campaign": "Soil: other campaign",
              "ossl_kssl_to_lucas": "Soil: KSSL→LUCAS", "corn_moisture": "Corn moisture", "corn_oil": "Corn oil",
              "corn_protein": "Corn protein", "corn_starch": "Corn starch", "tablets": "Tablets"}
ORDER = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
         "corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
KEY = ["GC-D", "SCP", "ASTM-R", "CV+", "WCP", "CQR", "G-W-A"]
style()


def summ():
    f = os.path.join(RESULTS, "summary_results.csv")
    return pd.read_csv(f) if os.path.exists(f) else None


# ------------------------------------------------------------------ Fig 1: method schematic
def fig_schematic():
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); ax.set_axis_off(); ax.set_xlim(0, 10); ax.set_ylim(0, 3.2)
    def box(x, y, w, h, t, fc="#f4f4f2", ec=INK2, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.8))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.6, color=INK, wrap=True,
                fontweight="bold" if bold else "normal")
    def arr(x1, y1, x2, y2):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.8))
    box(0.05, 2.0, 1.75, 1.0, "Training spectra\nfrom K groups\n(seasons, instruments,\nregions)")
    box(2.15, 2.0, 1.9, 1.0, "Leave-one-group-out\nPLS fits\n(unit-disjoint)")
    box(4.4, 2.35, 1.9, 0.65, "Out-of-group\nresiduals rᵢ")
    box(4.4, 1.55, 1.9, 0.65, "Diagnostics T²ᵢ, Qᵢ")
    box(6.65, 1.9, 1.55, 1.1, "Scale model\nσ(T², Q)\n(log-link GLM)")
    box(8.45, 1.9, 1.5, 1.1, "Group-balanced\nquantile q̂ of\n|rᵢ|/σᵢ, wᵢ=1/(K·N_g)")
    box(2.15, 0.2, 1.9, 1.0, "Final PLS model\n(all training data)")
    box(4.4, 0.2, 1.9, 1.0, "New-group spectrum x:\nŷ(x), T²(x), Q(x)")
    box(7.2, 0.2, 2.75, 1.0, "Interval  ŷ(x) ± q̂·σ(x)", fc="#cde2fb", ec=SLOTS[0], bold=True)
    arr(1.8, 2.5, 2.15, 2.5); arr(4.05, 2.6, 4.4, 2.65); arr(4.05, 2.3, 4.4, 1.9)
    arr(6.3, 2.65, 6.65, 2.6); arr(6.3, 1.9, 6.65, 2.2); arr(8.2, 2.45, 8.45, 2.45)
    arr(4.05, 0.7, 4.4, 0.7); arr(6.3, 0.7, 7.2, 0.7); arr(9.2, 1.9, 9.2, 1.2); arr(7.4, 1.9, 7.6, 1.2)
    arr(0.9, 2.0, 2.15, 0.7)
    save(fig, FIG, "fig1_method_schematic")


# ------------------------------------------------------------------ Fig 2: data overview
def fig_data():
    from src.data.loaders import load_mango, load_ossl
    mg = load_mango(); lu = load_ossl("LUCAS.SSL")
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4), gridspec_kw=dict(width_ratios=[1.3, 1.1, 1]))
    m = mg.meta.assign(y=mg.y)
    fr = m.drop_duplicates("unit")
    seasons = sorted(fr.season.unique())
    data = [fr[fr.season == s].y.values for s in seasons]
    bp = axs[0].boxplot(data, widths=0.55, patch_artist=True, showfliers=False,
                        medianprops=dict(color=INK, lw=1.2), whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
    for b in bp["boxes"]:
        b.set(facecolor="#b7d3f6", edgecolor=INK2, lw=0.6)
    c = fr.groupby("season").size()
    axs[0].set_xticks(range(1, len(seasons) + 1))
    axs[0].set_xticklabels([f"{s}\n{c[s]}" for s in seasons], fontsize=5.8)
    axs[0].set_xlabel("Season / number of fruit", fontsize=7)
    axs[0].set_ylabel("Dry matter (% w/w)"); axs[0].set_title("(a) Mango fruit DM by season")
    blk = lu.meta.block.astype(int).values
    shade = np.where(blk % 2 == 0, "#86b6ef", "#c3c2b7")  # alternating neutral tones; identity via labels
    axs[1].scatter(lu.meta.lon, lu.meta.lat, c=shade, s=0.4, rasterized=True, lw=0)
    for b in np.unique(blk):
        sel = blk == b
        axs[1].text(np.median(lu.meta.lon[sel]), np.median(lu.meta.lat[sel]), str(b + 1), fontsize=4.5,
                    ha="center", va="center", color=INK)
    axs[1].set_xlabel("Longitude (°)"); axs[1].set_ylabel("Latitude (°)"); axs[1].set_title("(b) LUCAS spatial blocks (k=30)")
    axs[1].grid(False)
    axs[2].hist(np.log10(lu.y + 0.01), bins=50, color="#86b6ef", edgecolor="white", lw=0.3)
    axs[2].set_xlabel("log₁₀(SOC % + 0.01)"); axs[2].set_ylabel("Samples"); axs[2].set_title("(c) LUCAS organic carbon")
    fig.tight_layout(); save(fig, FIG, "fig2_data_overview")


# ------------------------------------------------------------------ Fig 3: main coverage + IS dot plot
def fig_main(s):
    s = s[(s.alpha == 0.1) & s.task.isin(ORDER) & s.method.isin(KEY + ["ORACLE"])]
    tasks = [t for t in ORDER if t in set(s.task)]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 0.42 * len(tasks) + 1.3), sharey=True)
    off = np.linspace(-0.3, 0.3, len(KEY))
    for j, m in enumerate(KEY):
        d = s[s.method == m].set_index("task")
        ys = [i + off[j] for i, t in enumerate(tasks) if t in d.index]
        tt = [t for t in tasks if t in d.index]
        axs[0].errorbar(d.loc[tt, "coverage"], ys, xerr=[d.loc[tt, "coverage"] - d.loc[tt, "coverage_ci_lo"],
                        d.loc[tt, "coverage_ci_hi"] - d.loc[tt, "coverage"]], fmt="o", ms=3.6, color=color(m),
                        elinewidth=0.8, capsize=0, label=METHOD_LABEL[m], zorder=3 if m == "GC-D" else 2)
        orc = s[s.method == "ORACLE"].set_index("task").interval_score
        rel = d.loc[tt, "interval_score"] / orc.loc[tt]
        axs[1].plot(np.minimum(rel, 3.0), ys, "o", ms=3.6, color=color(m), zorder=3 if m == "GC-D" else 2)
        for yv, r in zip(ys, rel):
            if not np.isfinite(r) or r > 3:
                axs[1].text(3.02, yv, "∞" if not np.isfinite(r) else f"{r:.1f}", fontsize=5.5, va="center", color=INK2)
    axs[0].axvline(0.9, color=INK2, lw=0.8, ls="--"); axs[0].text(0.9, -0.85, "nominal 0.90", fontsize=6, color=INK2, ha="center")
    axs[0].set_yticks(range(len(tasks))); axs[0].set_yticklabels([TASK_SHORT[t] for t in tasks])
    axs[0].invert_yaxis(); axs[0].set_xlabel("Group-averaged coverage (95% CI over groups)")
    axs[1].axvline(1.0, color=INK2, lw=0.8, ls="--"); axs[1].set_xlabel("Interval score ÷ oracle interval score")
    axs[1].set_xlim(0.8, 3.15)
    h, l = axs[0].get_legend_handles_labels()
    axs[1].set_xlim(0.8, 3.25)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.legend(h, l, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.945))
    save(fig, FIG, "fig3_main_coverage_score")


# ------------------------------------------------------------------ Fig 4: per-group coverage
def fig_groups():
    f = os.path.join(RESULTS, "per_group_results.csv")
    if not os.path.exists(f):
        return
    pg = pd.read_csv(f)
    pg = pg[(pg.alpha == 0.1) & pg.method.isin(["SCP", "ASTM-R", "GC-D"])]
    tasks = [t for t in ["mango_season_loso", "mango_instrument", "mango_population", "ossl_lucas_block"] if t in set(pg.task)]
    if not tasks:
        return
    fig, axs = plt.subplots(1, len(tasks), figsize=(7.2, 2.3), sharey=True)
    axs = np.atleast_1d(axs)
    rng = np.random.default_rng(0)
    for ax, t in zip(axs, tasks):
        for j, m in enumerate(["ASTM-R", "SCP", "GC-D"]):
            v = pg[(pg.task == t) & (pg.method == m)].coverage.values
            ax.scatter(j + rng.uniform(-0.18, 0.18, len(v)), v, s=9, color=color(m), alpha=0.85, lw=0)
            ax.plot([j - 0.28, j + 0.28], [np.median(v)] * 2, color=INK, lw=1.2)
        ax.axhline(0.9, color=INK2, ls="--", lw=0.8)
        ax.set_xticks(range(3)); ax.set_xticklabels(["Classical", "Split CP", "GC-D"], rotation=30)
        ax.set_title(f"{TASK_SHORT[t]}\n({len(v)} groups)")
    axs[0].set_ylabel("Coverage in held-out group")
    fig.tight_layout(); save(fig, FIG, "fig4_per_group_coverage")


# ------------------------------------------------------------------ Fig 5: factorial ablation heatmap
def fig_ablation(s):
    cells = ["R-U-A", "R-U-D", "G-U-A", "G-W-A", "G-U-D", "GC-D"]
    s = s[(s.alpha == 0.1) & s.task.isin(ORDER) & s.method.isin(cells)]
    tasks = [t for t in ORDER if t in set(s.task)]
    cov = s.pivot(index="task", columns="method", values="coverage").loc[tasks, cells]
    isc = s.pivot(index="task", columns="method", values="interval_score").loc[tasks, cells]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 0.33 * len(tasks) + 1.2))
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    div = LinearSegmentedColormap.from_list("div", ["#c0392b", "#e34948", "#f3b0ad", "#f0efec", "#9ec5f4", "#2a78d6", "#184f95"])
    im = axs[0].imshow(cov.values - 0.9, cmap=div, norm=TwoSlopeNorm(0, -0.25, 0.1), aspect="auto")
    for i in range(len(tasks)):
        for j in range(len(cells)):
            axs[0].text(j, i, f"{cov.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color=INK)
    rel = isc.values / isc[["GC-D"]].values
    seq = LinearSegmentedColormap.from_list("seq", ["#f4f4f2", "#86b6ef", "#1c5cab"])
    axs[1].imshow(np.log(np.clip(rel, 0.5, 4)), cmap=seq, vmin=0, vmax=np.log(4), aspect="auto")
    for i in range(len(tasks)):
        for j in range(len(cells)):
            axs[1].text(j, i, f"{rel[i, j]:.2f}", ha="center", va="center", fontsize=6,
                        color="white" if rel[i, j] > 2.2 else INK)
    for ax, t in zip(axs, ["(a) Coverage (colour: deviation from 0.90)", "(b) Interval score relative to GC-D"]):
        ax.set_xticks(range(len(cells))); ax.set_xticklabels(cells, rotation=30); ax.grid(False); ax.set_title(t)
        ax.set_yticks(range(len(tasks))); ax.set_yticklabels([TASK_SHORT[x] for x in tasks])
    axs[1].set_yticklabels([])
    fig.text(0.5, -0.02, "R/G: random vs out-of-group calibration folds · U/W: uniform vs group-balanced weights · "
             "A/D: absolute vs diagnostic-normalised score", ha="center", fontsize=6.3, color=INK2)
    fig.tight_layout(); save(fig, FIG, "fig5_ablation")


# ------------------------------------------------------------------ Fig 6: robustness
def fig_robust():
    from matplotlib.ticker import NullFormatter, FixedLocator
    rd = os.path.join(RESULTS, "robustness")
    g = sorted(glob.glob(os.path.join(rd, "groups_*_K*_rep*.csv")))
    sz = sorted(glob.glob(os.path.join(rd, "size_frac*.csv")))
    pt = sorted(glob.glob(os.path.join(rd, "perturb_*.csv")))
    if not (g or sz or pt):
        return
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.9))
    if g:
        d = pd.concat([pd.read_csv(f) for f in g])
        d = d.groupby(["task", "method", "K", "rep"]).agg(coverage=("coverage", "mean"), fin=("finite_frac", "min")).reset_index()
        d = d.groupby(["task", "method", "K"]).agg(mean=("coverage", "mean"), fin=("fin", "min")).reset_index()
        for m in ["SCP", "G-W-A", "GC-D", "HJ+"]:
            for t, mk, ls in [("mango_instrument", "o", "-"), ("ossl_lucas_block", "s", "--")]:
                e = d[(d.method == m) & (d.task == t) & (d.fin >= 1)]
                if len(e):
                    axs[0].plot(e.K, e["mean"], ls=ls, marker=mk, ms=3.5, lw=1.4,
                                color=color(m) if m != "HJ+" else SLOTS[7])
        axs[0].axhline(0.9, color=INK2, ls=":", lw=0.8)
        axs[0].set_xscale("log"); axs[0].xaxis.set_major_locator(FixedLocator([3, 5, 10, 20]))
        axs[0].xaxis.set_minor_formatter(NullFormatter()); axs[0].set_xticklabels(["3", "5", "10", "20"])
        axs[0].set_xlabel("Training groups K"); axs[0].set_ylabel("Group-averaged coverage")
        axs[0].set_title("(a) Number of calibration groups")
        from matplotlib.lines import Line2D
        hs = [Line2D([], [], color=color(m) if m != "HJ+" else SLOTS[7], lw=1.4) for m in ["SCP", "G-W-A", "GC-D", "HJ+"]]
        hs += [Line2D([], [], color=INK2, marker="o", ls="-", ms=3), Line2D([], [], color=INK2, marker="s", ls="--", ms=3)]
        axs[0].legend(hs, ["Split CP", "Group CP abs.", "GC-D", "Hier. jackknife+ (finite only)", "mango instr.", "soil region"],
                      fontsize=5, loc="lower right")
    if sz:
        d = pd.concat([pd.read_csv(f) for f in sz])
        d = d.groupby(["method", "frac", "rep"]).coverage.mean().groupby(["method", "frac"]).agg(["mean", "std"]).reset_index()
        for m in ["SCP", "ASTM-R", "CV+", "G-W-A", "GC-D", "ORACLE"]:
            e = d[d.method == m]
            axs[1].errorbar(e.frac, e["mean"], yerr=e["std"], marker="o", ms=3, color=color(m), lw=1.4, capsize=0, label=METHOD_LABEL[m])
        axs[1].axhline(0.9, color=INK2, ls=":", lw=0.8)
        axs[1].set_xticks([0.1, 0.25, 0.5]); axs[1].set_xticklabels(["10 %", "25 %", "50 %"])
        axs[1].set_xlabel("Training fruit used"); axs[1].set_title("(b) Training-set size")
        axs[1].legend(fontsize=5, loc="center right")
    if pt:
        d = pd.concat([pd.read_csv(f) for f in pt])
        d = d.groupby(["perturbation", "level", "method"]).agg(coverage=("coverage", "mean")).reset_index()
        order = [("none", 0.0), ("gain", 0.02), ("gain", 0.05), ("offset_slope", 0.5), ("offset_slope", 2.0),
                 ("wl_shift", 0.5), ("wl_shift", 1.0), ("wl_shift", 2.0), ("noise", 0.01), ("noise", 0.03), ("noise", 0.1)]
        lab = {"none": "none", "gain": "gain ×", "offset_slope": "tilt", "wl_shift": "λ shift nm", "noise": "noise"}
        order = [o for o in order if ((d.perturbation == o[0]) & np.isclose(d.level, o[1])).any()]
        xs = np.arange(len(order))
        off = np.linspace(-0.25, 0.25, 4)
        for j, m in enumerate(["SCP", "ASTM-R", "G-W-A", "GC-D"]):
            v = [d[(d.perturbation == p) & np.isclose(d.level, l) & (d.method == m)].coverage.mean() for p, l in order]
            axs[2].plot(xs + off[j], v, "o", ms=3.5, color=color(m), label=METHOD_LABEL[m])
        for b in [0.5, 2.5, 4.5, 7.5]:
            axs[2].axvline(b, color=GRID, lw=0.8)
        axs[2].set_xticks(xs)
        axs[2].set_xticklabels([("none" if p == "none" else f"{lab[p]} {1 + l if p == 'gain' else l:g}") for p, l in order],
                               rotation=60, fontsize=5.5, ha="right")
        axs[2].axhline(0.9, color=INK2, ls=":", lw=0.8); axs[2].set_title("(c) Test-time perturbation (mango)")
        axs[2].legend(fontsize=5, loc="lower left"); axs[2].grid(axis="x", visible=False)
    fig.tight_layout(); save(fig, FIG, "fig6_robustness")


# ------------------------------------------------------------------ Fig 7: efficiency
def fig_efficiency(s=None):
    f = os.path.join(RESULTS, "timing_summary.csv")
    if not os.path.exists(f):
        return
    t = pd.read_csv(f).sort_values("method_s")
    shared = t.shared_setup_s.mean()
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    labels = [METHOD_LABEL.get(m, m) for m in t.method]
    axs[0].barh(labels, t.method_s + 1e-4, color=[color(m) for m in t.method], height=0.6)
    axs[0].set_xscale("log"); axs[0].set_xlabel("Method-specific time per held-out season (s)")
    axs[0].axvline(shared, color=INK2, ls="--", lw=0.8)
    axs[0].text(shared, len(t) - 0.4, f" shared group CV + PLS: {shared:.1f} s", fontsize=6, color=INK2, va="top")
    axs[1].barh(labels, t.peak_MiB, color=[color(m) for m in t.method], height=0.6)
    axs[1].set_xlabel("Peak additional memory (MiB)")
    fig.tight_layout(); save(fig, FIG, "fig7_efficiency")


# ------------------------------------------------------------------ Fig 8: error analysis
def fig_error():
    f = os.path.join(RESULTS, "error_analysis", "conditional_coverage_mango_season_loso.csv")
    g = os.path.join(RESULTS, "error_analysis", "group_bias_mango_instrument.csv")
    if not os.path.exists(f):
        return
    cc = pd.read_csv(f)
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.4))
    for ax, by, title in [(axs[0], "Q-ratio decile", "(a) by spectral residual Q (decile)"),
                          (axs[1], "reference decile", "(b) by reference DM (decile)")]:
        for m in ["SCP", "ASTM-R", "G-W-A", "GC-D"]:
            e = cc[(cc.by == by) & (cc.method == m)]
            ax.plot(np.arange(1, len(e) + 1), e.coverage, marker="o", ms=3, color=color(m), lw=1.4, label=METHOD_LABEL[m])
        ax.axhline(0.9, color=INK2, ls="--", lw=0.8); ax.set_xlabel("Decile"); ax.set_title(title)
    axs[0].set_ylabel("Coverage (mango, new season)"); axs[0].legend(fontsize=5)
    if os.path.exists(g):
        gb = pd.read_csv(g)
        for m in ["SCP", "GC-D"]:
            e = gb[gb.method == m]
            axs[2].scatter(np.abs(e.bias), e.coverage, s=12, color=color(m), label=METHOD_LABEL[m], lw=0)
        axs[2].axhline(0.9, color=INK2, ls="--", lw=0.8)
        axs[2].set_xlabel("|Mean prediction bias| in held-out instrument (% DM)")
        axs[2].set_title("(c) Instrument-level bias vs coverage"); axs[2].legend(fontsize=5)
    fig.tight_layout(); save(fig, FIG, "fig8_error_analysis")


# ------------------------------------------------------------------ Fig 9: decision analysis
def fig_decision():
    f = os.path.join(RESULTS, "decision", "spec_limit_decisions_mango_loso.csv")
    if not os.path.exists(f):
        return
    d = pd.read_csv(f); d = d[d.subset == "all"]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.4))
    for m in ["SCP", "ASTM-R", "CV+", "G-W-A", "GC-D", "ORACLE"]:
        e = d[d.method == m]
        axs[0].plot(e.limit, e.false_accept_among_accepted, marker="o", ms=3, color=color(m), label=METHOD_LABEL[m])
        axs[1].plot(e.limit, e.yield_of_compliant, marker="o", ms=3, color=color(m))
    axs[0].axhline(0.05, color=INK2, ls="--", lw=0.8)
    axs[0].set_xlabel("Specification limit L (% DM)"); axs[0].set_ylabel("False acceptances / accepted")
    axs[0].set_title("(a) Wrongly accepted 'DM ≥ L' decisions")
    axs[1].legend(*axs[0].get_legend_handles_labels(), fontsize=5, loc="upper right")
    axs[1].set_xlabel("Specification limit L (% DM)"); axs[1].set_ylabel("Accepted / truly compliant")
    axs[1].set_title("(b) Yield of compliant fruit")
    fig.tight_layout(); save(fig, FIG, "fig9_decisions")


# ------------------------------------------------------------------ Fig 10: effect sizes
def fig_effects():
    f = os.path.join(RESULTS, "comparisons_alpha0.1.csv")
    if not os.path.exists(f):
        return
    c = pd.read_csv(f)
    comps = ["SCP", "ASTM-R", "CV+", "WCP", "CQR", "G-W-A"]
    c = c[c.comparator.isin(comps) & c.task.isin(ORDER)]
    tasks = [t for t in ORDER if t in set(c.task)]
    fig, ax = plt.subplots(figsize=(7.2, 0.33 * len(tasks) + 1.2))
    off = np.linspace(-0.3, 0.3, len(comps))
    for j, m in enumerate(comps):
        e = c[c.comparator == m].set_index("task")
        tt = [t for t in tasks if t in e.index]
        ys = [tasks.index(t) + off[j] for t in tt]
        sig = e.loc[tt, "IS_p_holm"] < 0.05
        ax.scatter(e.loc[tt, "IS_r_rb"], ys, s=[22 if q else 10 for q in sig], color=color(m),
                   marker="o", label=f"vs {METHOD_LABEL[m]}", lw=0)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(tasks))); ax.set_yticklabels([TASK_SHORT[t] for t in tasks]); ax.invert_yaxis()
    ax.set_xlabel("Rank-biserial effect on interval score (negative = GC-D better); large dots: Holm p < 0.05")
    ax.legend(ncol=3, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, 1.25))
    fig.tight_layout(); save(fig, FIG, "fig10_effect_sizes")


if __name__ == "__main__":
    fig_schematic()
    try:
        fig_data()
    except Exception as e:
        print("fig_data failed:", e)
    s = summ()
    if s is not None:
        fig_main(s); fig_ablation(s); fig_efficiency(s)
    fig_groups(); fig_robust(); fig_error(); fig_decision(); fig_effects()
    print("figures written to", FIG)
