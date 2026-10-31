"""Analyses added in response to the reviewers (revision 1), computed from the result files of the main study and
of experiments/run_revision.py / run_simulation.py. Writes results/revision/*.csv and a summary JSON.

  units_per_group          R1.7   groups, physical units per group and units shared across groups, per scenario
  population_absorption    R1.11  are population effects subsumed by season/instrument effects?
  effect_size_intervals    R1.14  bootstrap CIs and Bayesian-bootstrap posterior probabilities of IS differences
  decisions                R1.16, R4.5  specification-limit decisions over a grid of limits, mango and soil, costs
  conditional_coverage     R1.5   G-W-A vs GC-D by decile of the Q ratio and of T², several scenarios
  alpha_consistency        R1.22  GC-D vs SCP coverage at nominal 0.80, 0.90 and 0.95
  coverage_dispersion      R4.1   between-group vs within-group (sampling) variance of per-group coverage
  uninformative_rule       R1.15, R4.2  intervals no narrower than the reference-value range; Q-limit rejection
  rejection_rule           R1.18  Q-limit rule on perturbed spectra (needs run_revision --exp reject)
  revision_experiments     summaries of scale-form, bias-correction, unbalanced, WCP and simulation experiments
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.utils import RESULTS

R = RESULTS; OUT = os.path.join(R, "revision"); os.makedirs(OUT, exist_ok=True)
MAIN = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
        "corn_moisture", "corn_oil", "corn_protein", "corn_starch"]
ALL = MAIN + ["ossl_lucas_campaign", "ossl_kssl_to_lucas", "tablets"]
SUMMARY = {}


def points(task, methods=None):
    d = pd.read_parquet(os.path.join(R, "main", f"points_{task}_seed0.parquet"))
    d = d[d.alpha == 0.1]
    return d if methods is None else d[d.method.isin(methods)]


# ------------------------------------------------------------------------------------------ R1.7
def units_per_group():
    from src.evaluation.tasks import get_task
    rows = []
    for t in ALL:
        task = get_task(t, seed=0)
        units = task["ds"].meta.unit.to_numpy()
        lab = np.full(len(units), None, dtype=object)
        for f in task["folds"]:
            lab[f["test"]] = f["test_group"][f["test"]].astype(str)
        m = lab != None  # noqa: E711
        d = pd.DataFrame(dict(unit=units[m], group=lab[m]))
        upg = d.groupby("group").unit.nunique()
        shared = (d.groupby("unit").group.nunique() > 1)
        cal = [len(np.unique(f["calib_group"][f["train"]])) for f in task["folds"]]
        rows.append(dict(task=t, held_out_groups=int(d.group.nunique()), spectra=int(m.sum()),
                         units=int(d.unit.nunique()), units_per_group_median=float(upg.median()),
                         units_per_group_min=int(upg.min()), units_per_group_max=int(upg.max()),
                         units_in_more_than_one_group=int(shared.sum()),
                         share_units_shared=float(shared.mean()), calibration_groups_min=int(min(cal)),
                         calibration_groups_max=int(max(cal))))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(OUT, "units_per_group.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.11
def population_absorption():
    """(a) Spread of population-mean residuals when the population is new but its season and instruments are in
    training (population scenario) vs when its whole season is new (LOSO), same fruit, GC-D centre = final PLS model.
    (b) Share of the between-population variance of those residual means explained by season (one-way ANOVA R²).
    (c) Share of the between-population variance of the population-mean PLS scores (model fitted on all spectra,
    A = 15) that is explained by season and instrument composition (least squares on season dummies and the
    instrument proportions of each population)."""
    from src.data.loaders import load_mango
    from src.models.pls import PLS1
    from src.evaluation.tasks import get_task
    meta = load_mango().meta
    res = {}
    for t in ["mango_population", "mango_season_loso"]:
        d = points(t, ["GC-D"])
        d = d.assign(r=d.y - d.yhat, population=meta.population.to_numpy()[d.idx], season=meta.season.to_numpy()[d.idx])
        pm = d.groupby("population").agg(r=("r", "mean"), season=("season", "first"), n=("r", "size"))
        res[t] = pm
    pp, pl = res["mango_population"], res["mango_season_loso"].loc[res["mango_population"].index]
    def r2_season(pm):
        sm = pm.groupby("season").r.transform(lambda v: np.average(v))
        return float(1 - np.sum((pm.r - sm) ** 2) / np.sum((pm.r - pm.r.mean()) ** 2))
    task = get_task("mango_population", seed=0)
    X = task["X"]; y = task["ds"].y.astype(float)
    S = PLS1(15).fit(X, y).set_n_lv(15).diagnostics(X)["scores"]
    P = pd.DataFrame(S).assign(population=meta.population.to_numpy()).groupby("population").mean()
    inst = pd.crosstab(meta.population, meta.instrument, normalize="index").loc[P.index]
    seas = pd.get_dummies(meta.groupby("population").season.first().loc[P.index]).astype(float)
    D = np.c_[np.ones(len(P)), seas.to_numpy()[:, 1:], inst.to_numpy()[:, 1:]]
    Pc = P.to_numpy() - P.to_numpy().mean(0)
    fit = D @ np.linalg.lstsq(D, P.to_numpy(), rcond=None)[0]
    r2_scores = float(1 - np.sum((P.to_numpy() - fit) ** 2) / np.sum(Pc ** 2))
    Ds = np.c_[np.ones(len(P)), seas.to_numpy()[:, 1:]]
    fit_s = Ds @ np.linalg.lstsq(Ds, P.to_numpy(), rcond=None)[0]
    r2_scores_season = float(1 - np.sum((P.to_numpy() - fit_s) ** 2) / np.sum(Pc ** 2))
    out = dict(n_populations=int(len(pp)), n_parameters_season_instrument=int(D.shape[1]),
               sd_pop_mean_residual_population_scenario=float(pp.r.std()),
               sd_pop_mean_residual_loso_scenario=float(pl.r.std()),
               r2_season_of_pop_residual_means_loso=r2_season(pl),
               r2_season_of_pop_residual_means_population=r2_season(pp),
               r2_pop_mean_scores_by_season=r2_scores_season,
               r2_pop_mean_scores_by_season_and_instruments=r2_scores,
               worst_population=str(pp.r.abs().idxmax()), worst_population_bias=float(pp.r.loc[pp.r.abs().idxmax()]))
    json.dump(out, open(os.path.join(OUT, "population_absorption.json"), "w"), indent=1)
    return out


def population_error_comparison():
    """Direct test of whether a new population brings extra error: RMSEP of the final PLS models for held-out
    populations, seasons and instruments (GC-D centre, seed 0) vs the random unit-wise 5-fold cross-validation error
    of the same data (PLS, A = median number of LVs selected in the population scenario)."""
    from src.evaluation.tasks import get_task
    from src.training.crossfit import CrossFit, make_folds
    task = get_task("mango_population", seed=0)
    X, y = task["X"], task["ds"].y.astype(float); meta = task["ds"].meta
    A = int(pd.read_csv(os.path.join(R, "main", "folds_mango_population_seed0.csv")).A.median())
    folds = make_folds(np.zeros(len(y)).astype(str), meta.unit.to_numpy(), "random", n_folds=5, seed=0)
    cf = CrossFit(X, y, folds, A)
    rmse_rand = float(np.sqrt(np.mean((y - cf.oof_at(A)) ** 2)))
    rows = [dict(scenario="random unit-wise 5-fold CV (no group shift)", rmsep=rmse_rand, A=A)]
    for t, lab in [("mango_population", "new population"), ("mango_season_loso", "new season"),
                   ("mango_season_forward", "next season"), ("mango_instrument", "new instrument")]:
        d = points(t, ["GC-D"])
        rows.append(dict(scenario=lab, rmsep=float(np.sqrt(np.mean((d.y - d.yhat) ** 2))),
                         A=float(pd.read_csv(os.path.join(R, "main", f"folds_{t}_seed0.csv")).A.median())))
    out = pd.DataFrame(rows); out["ratio_to_random_cv"] = out.rmsep / rmse_rand
    out.to_csv(os.path.join(OUT, "population_error_comparison.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.14
def effect_size_intervals(B=4000):
    pg = pd.read_csv(os.path.join(R, "per_group_results.csv")); raw = pd.read_csv(os.path.join(R, "raw_results.csv"))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from aggregate import analysis_units
    rng = np.random.default_rng(1)
    rows = []
    for t in MAIN:
        d0 = pg[(pg.task == t) & (pg.alpha == 0.1)]
        if t == "mango_population":
            r0 = raw[(raw.task == t) & (raw.alpha == 0.1) & (raw.seed == 0)]
            d = r0.groupby(["fold", "method"], as_index=False).interval_score.mean().assign(unit=lambda x: x.fold)
        else:
            d, _ = analysis_units(d0)
        piv = d.pivot_table(index="unit", columns="method", values="interval_score")
        for comp in ["SCP", "ASTM-R", "ASTM-G", "G-W-A", "CV+", "CQR"]:
            if comp not in piv:
                continue
            diff = (piv["GC-D"] - piv[comp]).dropna().to_numpy()
            if not np.isfinite(diff).all():
                continue
            n = len(diff)
            boot = np.array([rng.choice(diff, n).mean() for _ in range(B)])
            wts = rng.dirichlet(np.ones(n), size=B)            # Bayesian bootstrap (Rubin 1981)
            post = wts @ diff
            rel = diff / piv[comp].loc[(piv["GC-D"] - piv[comp]).dropna().index].to_numpy()
            rows.append(dict(task=t, comparator=comp, n_units=n, mean_diff=diff.mean(),
                             ci_lo=np.quantile(boot, 0.025), ci_hi=np.quantile(boot, 0.975),
                             rel_mean_diff=rel.mean(), share_units_gcd_lower=float(np.mean(diff < 0)),
                             post_prob_gcd_lower=float(np.mean(post < 0))))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(OUT, "effect_size_intervals.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.16 / R4.5
def decisions():
    rows = []
    specs = {"mango_season_loso": np.arange(12.0, 19.01, 0.5), "ossl_lucas_block": np.array([1.0, 1.5, 2.0, 3.0, 5.0, 8.0])}
    for t, Ls in specs.items():
        d = points(t, ["SCP", "ASTM-R", "ASTM-G", "CQR", "GC-D", "ORACLE"])
        for m, dm in d.groupby("method"):
            y, lo, yh = dm.y.to_numpy(), dm.lo.to_numpy(), dm.yhat.to_numpy()
            for L in Ls:
                acc = lo >= L; comp = y >= L
                rows.append(dict(task=t, method=m, L=L, share_compliant=comp.mean(),
                                 false_acceptance=float(np.mean(~comp[acc])) if acc.any() else np.nan,
                                 yield_compliant=float(np.mean(acc[comp])) if comp.any() else np.nan,
                                 p_accept_noncompliant=float(np.mean(acc & ~comp)), p_reject_compliant=float(np.mean(~acc & comp)),
                                 point_rule_false_acceptance=float(np.mean(~comp[yh >= L])) if (yh >= L).any() else np.nan,
                                 point_rule_yield=float(np.mean((yh >= L)[comp])) if comp.any() else np.nan))
    out = pd.DataFrame(rows)
    # break-even cost ratio c* (cost of a false acceptance / cost of a false rejection) above which GC-D has the lower
    # expected loss than the comparator:  c·Pa(GC) + Pr(GC) < c·Pa(X) + Pr(X)  ⇔  c > (Pr(GC) − Pr(X)) / (Pa(X) − Pa(GC))
    be = []
    for (t, L), g in out.groupby(["task", "L"]):
        gg = g.set_index("method")
        for comp in ["SCP", "ASTM-R", "ASTM-G"]:
            dPa = gg.loc[comp, "p_accept_noncompliant"] - gg.loc["GC-D", "p_accept_noncompliant"]
            dPr = gg.loc["GC-D", "p_reject_compliant"] - gg.loc[comp, "p_reject_compliant"]
            be.append(dict(task=t, L=L, comparator=comp, delta_false_accept=dPa, delta_false_reject=dPr,
                           break_even_cost_ratio=(dPr / dPa) if dPa > 0 else np.nan))
    out.to_csv(os.path.join(OUT, "decisions_grid.csv"), index=False)
    pd.DataFrame(be).to_csv(os.path.join(OUT, "decisions_break_even.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.5
def conditional_coverage():
    rows = []
    for t in ["mango_season_loso", "mango_season_forward", "mango_instrument", "ossl_lucas_block", "ossl_kssl_to_lucas"]:
        d = points(t, ["SCP", "ASTM-G", "G-W-A", "GC-D"])
        ref = d[d.method == "GC-D"]
        for var in ["Qr", "T2"]:
            edges = np.quantile(ref[var], np.linspace(0, 1, 11)); edges[-1] += 1e-9
            for m, dm in d.groupby("method"):
                b = np.clip(np.searchsorted(edges, dm[var].to_numpy(), side="right") - 1, 0, 9)
                cov = (dm.y >= dm.lo) & (dm.y <= dm.hi)
                for k in range(10):
                    s = b == k
                    rows.append(dict(task=t, by=var, decile=k + 1, method=m, coverage=float(cov[s].mean()),
                                     width=float((dm.hi - dm.lo)[s].mean()), n=int(s.sum())))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(OUT, "conditional_coverage.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.22
def alpha_consistency():
    s = pd.read_csv(os.path.join(R, "summary_results.csv"))
    s = s[s.method.isin(["SCP", "ASTM-R", "ASTM-G", "G-W-A", "GC-D"]) & s.task.isin(MAIN)]
    out = s.pivot_table(index=["task", "alpha"], columns="method", values="coverage").reset_index()
    out["nominal"] = 1 - out.alpha
    out["gcd_minus_scp"] = out["GC-D"] - out["SCP"]
    out.to_csv(os.path.join(OUT, "alpha_consistency.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R4.1
def coverage_dispersion():
    """Per-group coverage of GC-D (seed 0) vs the binomial sampling variance expected if every group had the same true
    coverage. Spectra of one fruit are not independent, so the sampling variance is computed with the number of
    physical units per group (conservative: it over-states sampling variance when spectra of a unit disagree)."""
    from src.data.loaders import load_mango, load_ossl
    rows = []
    for t in ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block"]:
        meta = load_mango().meta if t.startswith("mango") else load_ossl("LUCAS.SSL").meta
        d = points(t, ["GC-D", "SCP"])
        d = d.assign(unit=meta.unit.to_numpy()[d.idx], cov=(d.y >= d.lo) & (d.y <= d.hi))
        for m, dm in d.groupby("method"):
            g = dm.groupby("group").agg(c=("cov", "mean"), nu=("unit", "nunique"))
            tot = g.c.var(ddof=1)
            within = float(np.mean(g.c * (1 - g.c) / g.nu))
            rows.append(dict(task=t, method=m, n_groups=len(g), mean_coverage=g.c.mean(), sd_group_coverage=np.sqrt(tot),
                             expected_sampling_sd=np.sqrt(within), between_group_share=max(0.0, 1 - within / tot),
                             q10_group_coverage=g.c.quantile(0.1), share_groups_below_085=float(np.mean(g.c < 0.85))))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(OUT, "coverage_dispersion.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.15 / R4.2
def uninformative_rule():
    """Flag an interval as uninformative when its width is at least the central 90 % range of the training reference
    values (the interval says no more than 'a sample like the calibration samples'), and/or when Q/Q̃ exceeds the
    99 % quantile of the out-of-group calibration Q ratios of the same fold (diag_limits_*.csv)."""
    rows = []
    for t in ALL:
        lf = os.path.join(OUT, f"diag_limits_{t}.csv")
        if not os.path.exists(lf):
            continue
        lim = pd.read_csv(lf).set_index("fold")
        d = points(t, ["GC-D"])
        rng_w = d.fold.map(lim.y_hi - lim.y_lo); q99 = d.fold.map(lim.Qr99)
        wide = (d.hi - d.lo) >= rng_w; qflag = d.Qr > q99
        cov = (d.y >= d.lo) & (d.y <= d.hi)
        for name, flag in [("width ≥ reference range", wide), ("Q/Q̃ > 99 % limit", qflag), ("either", wide | qflag)]:
            keep = ~flag
            rows.append(dict(task=t, rule=name, share_flagged=float(flag.mean()), coverage_all=float(cov.mean()),
                             coverage_retained=float(cov[keep].mean()) if keep.any() else np.nan,
                             coverage_flagged=float(cov[flag].mean()) if flag.any() else np.nan,
                             rmse_retained=float(np.sqrt(np.mean((d.y - d.yhat)[keep] ** 2))) if keep.any() else np.nan,
                             rmse_flagged=float(np.sqrt(np.mean((d.y - d.yhat)[flag] ** 2))) if flag.any() else np.nan))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(OUT, "uninformative_rule.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ R1.18
def rejection_rule():
    f = os.path.join(OUT, "reject_points.parquet")
    if not os.path.exists(f):
        return None
    d = pd.read_parquet(f)
    rows = []
    for (k, lev), g in d.groupby(["perturbation", "level"]):
        for rule in ["rej_Q95", "rej_Q99", "rej_Q99_T2"]:
            rej = g[rule].to_numpy()
            rows.append(dict(perturbation=k, level=lev, rule=rule, rejected=float(rej.mean()),
                             coverage_all=float(g.cov_gcd.mean()), coverage_retained=float(g.cov_gcd[~rej].mean()) if (~rej).any() else np.nan,
                             scp_coverage_all=float(g.cov_scp.mean()),
                             rmse_retained=float(np.sqrt(np.mean(g.abs_err[~rej] ** 2))) if (~rej).any() else np.nan,
                             rmse_all=float(np.sqrt(np.mean(g.abs_err ** 2)))))
    out = pd.DataFrame(rows); out.to_csv(os.path.join(OUT, "rejection_rule.csv"), index=False)
    return out


# ------------------------------------------------------------------------------------------ experiment summaries
def revision_experiments():
    import glob
    res = {}
    fs = glob.glob(os.path.join(OUT, "scale_form_*.csv"))
    if fs:
        d = pd.concat(pd.read_csv(f) for f in fs)
        s = d.groupby(["task", "variant"]).agg(coverage=("coverage", "mean"), interval_score=("interval_score", "mean"),
                                               width=("width", "mean"), n_groups=("group", "nunique")).reset_index()
        s.to_csv(os.path.join(OUT, "scale_form_summary.csv"), index=False); res["scale_form"] = s
    fs = glob.glob(os.path.join(OUT, "bias_correction_*.csv"))
    if fs:
        d = pd.concat(pd.read_csv(f) for f in fs)
        # average over repetitions within group first, then over groups (group-averaged, like the main results)
        gm = d.groupby(["task", "variant", "k", "group"]).agg(coverage=("coverage", "mean"), interval_score=("interval_score", "mean"),
                                                             width=("width", "mean")).reset_index()
        s = gm.groupby(["task", "variant", "k"]).agg(coverage=("coverage", "mean"), coverage_q10=("coverage", lambda v: v.quantile(0.1)),
                                                    worst_group=("coverage", "min"), interval_score=("interval_score", "mean"),
                                                    width=("width", "mean"), n_groups=("group", "nunique")).reset_index()
        s.to_csv(os.path.join(OUT, "bias_correction_summary.csv"), index=False); res["bias"] = s
        gm.to_csv(os.path.join(OUT, "bias_correction_per_group.csv"), index=False)
    fs = glob.glob(os.path.join(OUT, "unbalanced_mango*_rep*.csv")) + glob.glob(os.path.join(OUT, "unbalanced_ossl*_rep*.csv"))
    fs = [f for f in fs if "sizes" not in f]
    if fs:
        d = pd.concat(pd.read_csv(f) for f in fs)
        d = d[d.alpha == 0.1]
        s = d.groupby(["task", "method"]).agg(coverage=("coverage", "mean"), interval_score=("interval_score", "mean"),
                                              interval_score_median=("interval_score", "median"), width=("width_mean", "mean"),
                                              width_median=("width_mean", "median")).reset_index()
        sz = pd.concat(pd.read_csv(f).assign(task=os.path.basename(f).split("unbalanced_sizes_")[1].rsplit("_rep", 1)[0])
                       for f in glob.glob(os.path.join(OUT, "unbalanced_sizes_*.csv")))
        s = s.merge(sz.groupby("task").agg(largest_share=("largest_share", "median"), max_min_ratio=("max_min_ratio", "median"),
                                           n_train=("n_train", "median")).reset_index(), on="task")
        s.to_csv(os.path.join(OUT, "unbalanced_summary.csv"), index=False); res["unbalanced"] = s
    fs = glob.glob(os.path.join(OUT, "wcp_variants_*.csv"))
    if fs:
        d = pd.concat(pd.read_csv(f) for f in fs)
        s = d.groupby(["task", "estimator", "cap"]).agg(coverage=("coverage", "mean"), finite_frac=("finite_frac", "mean"),
                                                       interval_score=("interval_score", "mean"), ess_frac=("ess_frac", "median"),
                                                       test_mass_gt_alpha=("test_mass_gt_alpha", "mean"),
                                                       clf_auc=("clf_auc", "median")).reset_index()
        s.to_csv(os.path.join(OUT, "wcp_variants_summary.csv"), index=False); res["wcp"] = s
    return res


if __name__ == "__main__":
    which = sys.argv[1:] or ["units_per_group", "population_absorption", "effect_size_intervals", "decisions",
                             "conditional_coverage", "alpha_consistency", "coverage_dispersion", "uninformative_rule",
                             "rejection_rule", "revision_experiments"]
    for w in which:
        try:
            r = globals()[w]()
        except (FileNotFoundError, KeyError, IndexError, ValueError) as e:   # quick mode runs only a subset of scenarios
            print(f"== {w}: skipped ({type(e).__name__}: {e})")
            continue
        print(f"== {w}")
        if isinstance(r, pd.DataFrame):
            print(r.round(3).to_string(max_rows=60))
        elif isinstance(r, dict):
            for k, v in r.items():
                print(k, v.round(3).to_string(max_rows=80) if isinstance(v, pd.DataFrame) else v)
