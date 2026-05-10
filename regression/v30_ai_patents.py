"""
v3.0 - AI patent intensity as country-level AI-capacity instrument.

Use country AI patent applications per million people (OWID 2021,
sourced from WIPO via Stanford AI Index lineage) as a pre-period
country-level proxy for AI capacity. This is independent of GenAI
usage (Eurostat 2025) and independent of BLS/Eurostat occupational
employment.

H4-info-mediated-by-AI prediction:
  beta(H_info x ai_patents) > 0
  -- H_info effect should be stronger in countries with greater AI
  capacity, IF the post-2022 acceleration is driven by AI capacity
  rather than uniform diffusion.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
tsv = os.path.join(base, "data/eurostat_lfsa_egai2d.tsv")
patents_csv = os.path.join(base, "data/owid_ai_patents.csv")

print("[1/5] Loading AI patent data (OWID, 2021)...")
pat = pd.read_csv(patents_csv)
pat.columns = ["country_name", "code3", "year", "patents_per_M"]
pat = pat[pat["year"] == 2021]
pat = pat[~pat["country_name"].isin(
    ["World", "Asia", "Europe", "Africa", "North America",
     "South America", "European Union (27)"])]
print(f"  Country rows (2021): {len(pat)}")
print(f"  Top 5: {pat.nlargest(5, 'patents_per_M')[['country_name', 'patents_per_M']].to_string(index=False)}")

# ISO3 -> Eurostat geo
ISO3_TO_GEO = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "HRV": "HR", "CYP": "CY",
    "CZE": "CZ", "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR",
    "DEU": "DE", "GRC": "EL", "HUN": "HU", "IRL": "IE", "ITA": "IT",
    "LVA": "LV", "LTU": "LT", "LUX": "LU", "MLT": "MT", "NLD": "NL",
    "POL": "PL", "PRT": "PT", "ROU": "RO", "SVK": "SK", "SVN": "SI",
    "ESP": "ES", "SWE": "SE", "ISL": "IS", "NOR": "NO", "CHE": "CH",
    "GBR": "UK", "TUR": "TR",
}
pat["geo"] = pat["code3"].map(ISO3_TO_GEO)
pat = pat.dropna(subset=["geo"])
print(f"  After geo mapping: {len(pat)} EU/EEA countries")

print("\n[2/5] Loading Eurostat ISCO 2-digit panel...")
df = pd.read_csv(tsv, sep="\t", na_values=[":"], dtype=str)
key_col = df.columns[0]
year_cols = [c for c in df.columns if c.strip().isdigit()]
key_parts = df[key_col].str.split(",", expand=True)
key_parts.columns = ["freq", "isco08", "age", "sex", "unit", "geo"]
df = pd.concat([key_parts, df.drop(columns=[key_col])], axis=1)
df = df[(df["sex"] == "T") & (df["age"] == "Y15-64")
        & (df["unit"] == "THS_PER")].copy()


def to_num(v):
    if v is None or pd.isna(v):
        return np.nan
    s = str(v).strip()
    if s in ("", ":", "u"):
        return np.nan
    s = s.split()[0]
    try:
        return float(s)
    except ValueError:
        return np.nan


for y in year_cols:
    df[y] = df[y].map(to_num)
years = [y.strip() for y in year_cols]
y2019 = year_cols[years.index("2019")]
y2024 = year_cols[years.index("2024")]


def isco2_code(c):
    s = str(c).strip()
    if s.startswith("OC") and len(s) == 4 and s[2:].isdigit():
        return s[2:]
    return None


df["isco2"] = df["isco08"].map(isco2_code)
df = df[df["isco2"].notna()].copy()

H_INFO_ISCO2 = {
    "11": +2.0, "12": +1.5, "13": +1.5, "14": +1.0,
    "21": +2.0, "22": +2.0, "23": +1.5, "24": +1.5, "25": +1.0, "26": +2.0,
    "31": +0.5, "32": +0.5, "33":  0.0, "34": +0.5, "35":  0.0,
    "41": -2.0, "42": -1.5, "43": -2.0, "44": -1.5,
    "51":  0.0, "52": -0.5, "53": +0.5, "54":  0.0,
    "61": +0.5, "62": +0.5, "63":  0.0,
    "71": +0.5, "72":  0.0, "73":  0.0, "74": +0.5, "75": -0.5,
    "81": -1.5, "82": -2.0, "83": -0.5,
    "91": -1.5, "92": -1.0, "93": -1.0, "94": -1.5, "95": -1.0, "96": -1.0,
}
df["H_info"] = df["isco2"].map(H_INFO_ISCO2)
df = df.dropna(subset=["H_info"])

panel = df[["geo", "isco2", "H_info", y2019, y2024]].copy()
panel.columns = ["geo", "isco2", "H_info", "emp_2019", "emp_2024"]
panel = panel.dropna(subset=["emp_2019", "emp_2024"])
panel = panel[(panel["emp_2019"] > 1) & (panel["emp_2024"] > 1)]
panel["delta_ann"] = (panel["emp_2024"] / panel["emp_2019"]) ** (1/5) - 1

print("[3/5] Merging panel with AI patents...")
panel = panel.merge(pat[["geo", "patents_per_M"]], on="geo", how="inner")
panel["log_patents"] = np.log1p(panel["patents_per_M"])
panel["z_log_patents"] = stats.zscore(panel["log_patents"])
panel["z_H_info"] = stats.zscore(panel["H_info"])
print(f"  Final panel: N = {len(panel):,}, "
      f"countries = {panel['geo'].nunique()}, "
      f"ISCO 2-digit = {panel['isco2'].nunique()}")


def ols(X, y):
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    sigma2 = (res ** 2).sum() / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = b / se
    p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))
    p_one = 1 - stats.t.cdf(t[1], n - k)
    r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, se, t, p_two, p_one, r2


print("\n[4/5] Regressions (country FE)...")
y = panel["delta_ann"].to_numpy()
ones = np.ones(len(panel))
ctry_d = pd.get_dummies(panel["geo"], prefix="cty",
                         drop_first=True).astype(float)

# Spec 1: H_info only with country FE (replicate v2.7 baseline on this sample)
X1 = np.column_stack([ones, panel["H_info"].to_numpy(), ctry_d.to_numpy()])
b1, se1, t1, p_two1, p_one1, r2_1 = ols(X1, y)
print(f"\n[Spec 1] delta_emp ~ H_info + country FE")
print(f"  beta(H_info) = {b1[1]:+.4e}  t = {t1[1]:+.3f}  p_one = {p_one1:.4g}  R^2 = {r2_1:.4f}")

# Spec 2: + H_info x AI patents interaction
panel["interaction"] = panel["H_info"] * panel["z_log_patents"]
X2 = np.column_stack([ones, panel["H_info"].to_numpy(),
                      panel["interaction"].to_numpy(), ctry_d.to_numpy()])
b2, se2, t2, p_two2, _, r2_2 = ols(X2, y)
p_one2_int = 1 - stats.t.cdf(t2[2], len(panel) - X2.shape[1])
print(f"\n[Spec 2] + H_info x AI_patents interaction (country FE)")
print(f"  beta(H_info)        = {b2[1]:+.4e}  t = {t2[1]:+.3f}  p2 = {p_two2[1]:.4g}")
print(f"  beta(INTERACTION)   = {b2[2]:+.4e}  t = {t2[2]:+.3f}  "
      f"p2 = {p_two2[2]:.4g}  p_one(b>0) = {p_one2_int:.4g}")
print(f"  R^2 = {r2_2:.4f}")

# Spec 3: tertile sub-samples by AI patents
print(f"\n[5/5] Tertile sub-samples by AI patent intensity")
# Compute country tertiles (not row tertiles)
cty_pat = panel.groupby("geo")["log_patents"].first().reset_index()
cty_pat["tertile"] = pd.qcut(cty_pat["log_patents"], 3,
                              labels=["bottom", "mid", "top"])
panel = panel.merge(cty_pat[["geo", "tertile"]], on="geo")

for t_lab in ["bottom", "mid", "top"]:
    sub = panel[panel["tertile"] == t_lab]
    if len(sub) < 50:
        continue
    X = np.column_stack([np.ones(len(sub)), sub["H_info"].to_numpy()])
    yy = sub["delta_ann"].to_numpy()
    b, se, t, p_two, p_one, r2 = ols(X, yy)
    print(f"  {t_lab:6s} AI-patents tertile (N={len(sub):4d}, "
          f"countries={sub['geo'].nunique():2d}): beta = {b[1]:+.4e}  "
          f"t = {t[1]:+.3f}  p_one = {p_one:.4g}")

# Save
out = {
    "v3.0_ai_patents": {
        "N": int(len(panel)), "n_countries": int(panel["geo"].nunique()),
        "ai_patent_data": "OWID AI patents per million 2021 (WIPO via Stanford lineage)",
        "spec_1_baseline": {"beta": float(b1[1]), "t": float(t1[1]),
                             "p_one": float(p_one1), "R2": float(r2_1)},
        "spec_2_interaction": {
            "beta_H_info": float(b2[1]),
            "beta_interaction": float(b2[2]),
            "se_interaction": float(se2[2]),
            "t_interaction": float(t2[2]),
            "p_two_interaction": float(p_two2[2]),
            "p_one_positive_interaction": float(p_one2_int),
            "R2": float(r2_2),
        },
    },
}
with open(os.path.join(base, "v30_ai_patents_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n  Saved -> v30_ai_patents_results.json")
