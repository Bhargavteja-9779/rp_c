"""Dataset loaders.

Every loader returns a :class:`SpectralDataset` with
    X          float32 array (n_spectra, n_wavelengths)
    y          float64 array (n_spectra,)  reference values
    wl         wavelengths (nm)
    meta       pandas DataFrame, one row per spectrum, with at least the column
               ``unit`` (the physical sample: fruit / soil sample / tablet / corn sample).
               Additional columns hold grouping variables used to define shift tasks.

Raw files are expected in ``data/raw`` (see ``scripts/download_data.py``). Parsed arrays are
cached as compressed ``.npz`` + ``.parquet`` files in ``data/processed``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")


@dataclass
class SpectralDataset:
    name: str
    X: np.ndarray
    y: np.ndarray
    wl: np.ndarray
    meta: pd.DataFrame
    target: str = ""
    units: str = ""
    info: dict = field(default_factory=dict)

    def subset(self, idx):
        idx = np.asarray(idx)
        return SpectralDataset(self.name, self.X[idx], self.y[idx], self.wl,
                               self.meta.iloc[idx].reset_index(drop=True), self.target, self.units, self.info)

    def __len__(self):
        return len(self.y)


def _cache(name):
    return os.path.join(PROC, f"{name}.npz"), os.path.join(PROC, f"{name}_meta.parquet")


def _save(ds: SpectralDataset):
    os.makedirs(PROC, exist_ok=True)
    a, b = _cache(ds.name)
    np.savez_compressed(a, X=ds.X, y=ds.y, wl=ds.wl)
    ds.meta.to_parquet(b)


def _load_cached(name, target, units, info=None):
    a, b = _cache(name)
    if os.path.exists(a) and os.path.exists(b):
        z = np.load(a)
        return SpectralDataset(name, z["X"], z["y"], z["wl"], pd.read_parquet(b), target, units, info or {})
    return None


# --------------------------------------------------------------------------------------------
# Mango dry matter (Anderson, Walsh, Subedi, Walsh; Mendeley Data 10.17632/46htwnp833.5)
# --------------------------------------------------------------------------------------------
def load_mango(wl_min: float = 684.0, wl_max: float = 990.0) -> SpectralDataset:
    """Mango DMC v4 file: 85,401 spectra of 10,560 fruit, seasons 2015-2021, 31 instruments.

    The wavelength window 684-990 nm is fixed a priori (the short-wave NIR region used for
    intact-fruit DM models with this instrument family)."""
    name = f"mango_v4_{int(wl_min)}_{int(wl_max)}"
    ds = _load_cached(name, "dry matter", "% w/w")
    if ds is not None:
        return ds
    p = os.path.join(RAW, "MangoDMC_NIR_Data_v4.parquet")
    df = pd.read_parquet(p) if os.path.exists(p) else pd.read_csv(os.path.join(RAW, "MangoDMC_NIR_Data_v4.csv"), low_memory=False)
    wcols = [c for c in df.columns if c.replace(".", "").isdigit()]
    wl = np.array([float(c) for c in wcols])
    keep = (wl >= wl_min) & (wl <= wl_max)
    X = df[np.array(wcols)[keep]].to_numpy(np.float32)
    meta = pd.DataFrame({
        "unit": df["reference_no"].astype(str).values,
        "season": df["season"].astype(int).values,
        "instrument": df["instrument"].astype(str).values,
        "population": df["population"].astype(str).values,
        "cultivar": df["cultivar"].astype(str).values,
        "region": df["region"].astype(str).values,
        "physio_stage": df["physio_stage"].astype(str).values,
        "temp": df["temp"].astype(str).values,
        "origin": df["origin"].astype(str).values,
        "outlier_flag": df["outlier_flag_1"].astype(int).values,
        "partition_ext": df["partition_ext"].fillna("").astype(str).values,
    })
    ds = SpectralDataset(name, X, df["dry_matter"].to_numpy(float), wl[keep], meta, "dry matter", "% w/w")
    _save(ds)
    return ds


# --------------------------------------------------------------------------------------------
# Open Soil Spectral Library v1.2 (vis-NIR, LUCAS and KSSL subsets)
# --------------------------------------------------------------------------------------------
def load_ossl(library: str = "LUCAS.SSL", step_nm: int = 10, n_blocks: int = 30,
              seed: int = 0) -> SpectralDataset:
    """Soil organic carbon (wt%) from vis-NIR reflectance (400-2500 nm, resampled every ``step_nm``).

    Spectra are converted to apparent absorbance log10(1/R). For LUCAS, ``block`` is a spatial
    group obtained by k-means (fixed seed) on (latitude, longitude*cos(latitude)); ``campaign`` is
    the survey year (2009 or 2015)."""
    lib_tag = library.split(".")[0].lower()
    name = f"ossl_{lib_tag}_{step_nm}nm"
    ds = _load_cached(name, "organic carbon", "% w/w")
    if ds is not None:
        return ds
    from sklearn.cluster import KMeans
    vis = pd.read_csv(os.path.join(RAW, "ossl_visnir_L0_v1.2.csv.gz"), low_memory=False)
    vis = vis[vis["dataset.code_ascii_txt"] == library]
    lab = pd.read_csv(os.path.join(RAW, "ossl_soillab_L1_v1.2.csv.gz"), low_memory=False,
                      usecols=["id.layer_uuid_txt", "oc_usda.c729_w.pct"])
    site = pd.read_csv(os.path.join(RAW, "ossl_soilsite_L0_v1.2.csv.gz"), low_memory=False,
                       usecols=["id.layer_uuid_txt", "longitude.point_wgs84_dd", "latitude.point_wgs84_dd",
                                "observation.date.begin_iso.8601_yyyy.mm.dd", "layer.upper.depth_usda_cm",
                                "id.project_ascii_txt"])
    df = vis.merge(lab, on="id.layer_uuid_txt", how="inner").merge(site, on="id.layer_uuid_txt", how="left")
    wcols = [c for c in df.columns if c.startswith("scan_visnir.") and c.endswith("_ref")]
    wl_all = np.array([int(c.split(".")[1].split("_")[0]) for c in wcols])
    sel = (wl_all >= 400) & (wl_all <= 2500) & ((wl_all - 400) % step_nm == 0)
    R = df[np.array(wcols)[sel]].to_numpy(float)
    y = df["oc_usda.c729_w.pct"].to_numpy(float)
    ok = np.isfinite(R).all(1) & np.isfinite(y) & (y >= 0) & (R > 0).all(1) & (R < 1.5).all(1)
    df, R, y = df[ok].reset_index(drop=True), R[ok], y[ok]
    X = np.log10(1.0 / R).astype(np.float32)
    lat = df["latitude.point_wgs84_dd"].to_numpy(float)
    lon = df["longitude.point_wgs84_dd"].to_numpy(float)
    meta = pd.DataFrame({"unit": df["id.layer_uuid_txt"].astype(str).values, "lat": lat, "lon": lon,
                         "campaign": df["observation.date.begin_iso.8601_yyyy.mm.dd"].astype(str).str[:4].values,
                         "depth_upper": df["layer.upper.depth_usda_cm"].to_numpy(float),
                         "project": df["id.project_ascii_txt"].astype(str).values})
    geo_ok = np.isfinite(lat) & np.isfinite(lon)
    block = np.full(len(df), -1)
    if geo_ok.sum() > n_blocks:
        coords = np.c_[lat[geo_ok], lon[geo_ok] * np.cos(np.deg2rad(lat[geo_ok]))]
        block[geo_ok] = KMeans(n_clusters=n_blocks, n_init=10, random_state=seed).fit_predict(coords)
    meta["block"] = block.astype(str)
    ds = SpectralDataset(name, X, y, wl_all[sel].astype(float), meta, "organic carbon", "% w/w",
                         {"library": library})
    _save(ds)
    return ds


# --------------------------------------------------------------------------------------------
# Corn (Cargill; distributed by Eigenvector Research): 80 samples x 3 instruments
# --------------------------------------------------------------------------------------------
CORN_PROPS = ["moisture", "oil", "protein", "starch"]


def load_corn(prop: str = "protein") -> SpectralDataset:
    import scipy.io as sio
    m = sio.loadmat(os.path.join(RAW, "corn.mat"), squeeze_me=True, struct_as_record=False)
    j = CORN_PROPS.index(prop)
    y80 = m["propvals"].data[:, j].astype(float)
    wl = np.arange(1100, 2500, 2, dtype=float)
    Xs, metas, ys = [], [], []
    for inst in ["m5", "mp5", "mp6"]:
        Xs.append(m[f"{inst}spec"].data.astype(np.float32))
        ys.append(y80)
        metas.append(pd.DataFrame({"unit": [f"corn{i:02d}" for i in range(80)], "instrument": inst}))
    return SpectralDataset(f"corn_{prop}", np.vstack(Xs), np.concatenate(ys), wl,
                           pd.concat(metas, ignore_index=True), prop, "% w/w")


# --------------------------------------------------------------------------------------------
# IDRC 2002 pharmaceutical tablet shoot-out (distributed by Eigenvector Research)
# --------------------------------------------------------------------------------------------
def load_tablets(prop: str = "assay") -> SpectralDataset:
    import scipy.io as sio
    t = sio.loadmat(os.path.join(RAW, "nir_shootout_2002.mat"), squeeze_me=True, struct_as_record=False)
    j = ["weight", "hardness", "assay"].index(prop)
    wl = np.arange(600, 1900, 2, dtype=float)
    Xs, ys, metas = [], [], []
    for part in ["calibrate", "validate", "test"]:
        Y = t[f"{part}_Y"].data[:, j].astype(float)
        for inst in (1, 2):
            X = t[f"{part}_{inst}"].data.astype(np.float32)
            Xs.append(X)
            ys.append(Y)
            metas.append(pd.DataFrame({"unit": [f"{part}{i:03d}" for i in range(len(Y))],
                                       "instrument": str(inst), "partition": part}))
    return SpectralDataset(f"tablets_{prop}", np.vstack(Xs), np.concatenate(ys), wl,
                           pd.concat(metas, ignore_index=True), prop, "mg")
