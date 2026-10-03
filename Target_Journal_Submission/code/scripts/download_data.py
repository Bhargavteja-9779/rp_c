"""Download all raw data sets into data/raw (≈ 470 MB). Re-running skips files that already exist.

Sources (all public):
  Mango DMC v5 (file MangoDMC_NIR_Data_v4.csv), Mendeley Data, CC BY 4.0, doi:10.17632/46htwnp833.5
  Corn and IDRC-2002 tablet shoot-out data, Eigenvector Research data-set page
  Open Soil Spectral Library v1.2 (vis-NIR, soil lab, soil site tables), Soil Spectroscopy for Global Good
"""
import hashlib, os, sys, urllib.request, zipfile

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
FILES = [
    ("MangoDMC_NIR_Data_v4.csv", "https://data.mendeley.com/public-files/datasets/46htwnp833/files/747b2613-4d0a-4628-8aaf-8fc5547d286e/file_downloaded",
     "367c377255c350f322387236ed121629807055baa3f02aeaf5a76fe9ada518b6"),
    ("corn.mat_.zip", "https://eigenvector.com/wp-content/uploads/2019/06/corn.mat_.zip", None),
    ("nir_shootout_2002.mat_.zip", "https://eigenvector.com/wp-content/uploads/2019/06/nir_shootout_2002.mat_.zip", None),
    ("ossl_visnir_L0_v1.2.csv.gz", "https://storage.googleapis.com/soilspec4gg-public/ossl_visnir_L0_v1.2.csv.gz", None),
    ("ossl_soillab_L1_v1.2.csv.gz", "https://storage.googleapis.com/soilspec4gg-public/ossl_soillab_L1_v1.2.csv.gz", None),
    ("ossl_soilsite_L0_v1.2.csv.gz", "https://storage.googleapis.com/soilspec4gg-public/ossl_soilsite_L0_v1.2.csv.gz", None),
]
# SHA-256 of the files used in the paper (checked after download; a mismatch is reported, not fatal,
# because upstream providers may re-issue files).
EXPECTED = {
    "corn.mat": "e28fd4be274a54ca57b1f2c67ef5a8bf4981f8314bcc73e4c64836fe658c46b5",
    "nir_shootout_2002.mat": "129a32ec9e194e568cbd96a200c88aabeb347156081b5dfbb0120372fdd6c22a",
    "ossl_soillab_L1_v1.2.csv.gz": "29554a5aab85e942373885d1f300c84caa94e7888ee28f0f44a6d9cc7bce80d9",
    "ossl_soilsite_L0_v1.2.csv.gz": "7dffacfbbce8f1d77b5f76f33b2182e963bb846bcd8e56a0df1fa0dc6974b6b2",
    "ossl_visnir_L0_v1.2.csv.gz": "e5a08c0deda182b7c123505c9f39adf9f5c9f6313c0022e74c51bc1f10b27a83",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(RAW, exist_ok=True)
    for name, url, sha in FILES:
        p = os.path.join(RAW, name)
        if not os.path.exists(p) and not os.path.exists(p.replace("_.zip", "")):
            print("downloading", name)
            urllib.request.urlretrieve(url, p)
        if name.endswith("_.zip") and os.path.exists(p):
            with zipfile.ZipFile(p) as z:
                for m in z.namelist():
                    if m.endswith(".mat") and not m.startswith("__MACOSX"):
                        z.extract(m, RAW)
        target = p.replace("_.zip", "") if name.endswith("_.zip") else p
        exp = sha or EXPECTED.get(os.path.basename(target))
        if exp and os.path.exists(target):
            got = sha256(target)
            print(f"{os.path.basename(target)}: sha256 {'OK' if got == exp else 'MISMATCH ' + got}")


if __name__ == "__main__":
    main()
