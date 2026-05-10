"""
v2.6 - Cross-country replication using Eurostat ISCO-08 employment panel.

Test whether the H4-info pattern observed on the US BLS panel
generalises to European labor markets. Use Eurostat LFSA_EGAI2D
(employment by 2-digit ISCO-08 occupation x country x year).

H_info proxy at ISCO 1-digit level is assigned via Acemoglu-Autor
routine-task mapping (manual scoring of the 10 ISCO major groups).
The mapping is constructed without any AI-exposure data.

Regression:
  delta_emp_log_{c,o} ~ alpha + beta * H_info_isco_o
                      + country_FE + occupation_FE + epsilon
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
tsv = os.path.join(base, "data/eurostat_lfsa_egai2d.tsv")

print("[1/6] Parsing Eurostat tsv...")
df = pd.read_csv(tsv, sep="\t", na_values=[":"], dtype=str)
key_col = df.columns[0]
year_cols = [c for c in df.columns if c.strip().isdigit()]
print(f"  rows: {len(df):,}, year columns: {len(year_cols)}")

# Split key column
key_parts = df[key_col].str.split(",", expand=True)
key_parts.columns = ["freq", "isco08", "age", "sex", "unit", "geo"]
df = pd.concat([key_parts, df.drop(columns=[key_col])], axis=1)

# Filter: T (total sex), Y15-64, THS_PER
mask = ((df["sex"] == "T") & (df["age"] == "Y15-64")
        & (df["unit"] == "THS_PER"))
df = df[mask].copy()
print(f"  after filter (T, Y15-64, THS_PER): {len(df):,}")

print("[2/6] Cleaning numeric values (handling 'b', 'u' flags)...")
# Cells like "8.3 b", "0.6 u", ":" or empty -> numeric
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

# Identify which years have data and select 2019, 2024
years_clean = [y.strip() for y in year_cols]
print(f"  years available: {years_clean[:3]} ... {years_clean[-3:]}")
year_2019 = year_cols[years_clean.index("2019")]
year_2024 = year_cols[years_clean.index("2024")]
print(f"  using {year_2019.strip()} and {year_2024.strip()}")

print("[3/6] Filtering ISCO-08 1-digit and computing H_info_ISCO...")
# Keep 1-digit ISCO codes (single character 0-9, then OC9, etc.)
# In Eurostat, 1-digit ISCO are coded as 'OC0' .. 'OC9' or just '0'..'9'.
# Inspect sample of isco codes:
isco_codes = sorted(df["isco08"].unique())
print(f"  ISCO codes sample (first 25): {isco_codes[:25]}")

# Try several patterns: keep numeric 1-digit codes (single digit) or "OC[0-9]"
def isco1_code(c):
    s = str(c).strip()
    if s.startswith("OC") and len(s) == 3 and s[-1].isdigit():
        return s[-1]
    if len(s) == 1 and s.isdigit():
        return s
    return None


df["isco1"] = df["isco08"].map(isco1_code)
df1 = df[df["isco1"].notna()].copy()
print(f"  ISCO 1-digit rows: {len(df1):,}")

# H_info_ISCO mapping (Acemoglu-Autor RTI inverse):
H_INFO_ISCO = {
    "1": +1.5,  # Managers: non-routine cognitive interactive
    "2": +1.5,  # Professionals: non-routine analytic
    "3": +0.5,  # Technicians: mixed cognitive
    "4": -1.5,  # Clerical: routine cognitive
    "5": 0.0,   # Services and sales: mixed
    "6": 0.0,   # Skilled agricultural: mixed
    "7": -0.5,  # Craft: routine + non-routine manual mix
    "8": -1.0,  # Plant and machine operators: routine manual
    "9": -1.5,  # Elementary: routine manual
    "0": np.nan,  # Armed forces: exclude
}
df1["H_info_isco"] = df1["isco1"].map(H_INFO_ISCO)
df1 = df1.dropna(subset=["H_info_isco"])

print("[4/6] Building country x occupation panel for 2019 vs 2024...")
panel = df1[["geo", "isco1", "H_info_isco", year_2019, year_2024]].copy()
panel = panel.rename(columns={year_2019: "emp_2019", year_2024: "emp_2024"})
panel = panel.dropna(subset=["emp_2019", "emp_2024"])
panel = panel[(panel["emp_2019"] > 1) & (panel["emp_2024"] > 1)]  # at least 1k workers
panel["delta_emp_log"] = np.log(panel["emp_2024"] / panel["emp_2019"]).clip(-2, 2)
panel["delta_emp_ann"] = (panel["emp_2024"] / panel["emp_2019"]) ** (1/5) - 1

print(f"  Final panel: N = {len(panel):,}, "
      f"countries = {panel['geo'].nunique()}, "
      f"ISCO 1-digit = {panel['isco1'].nunique()}")
print(f"\n  H_info distribution:")
print(panel.groupby("isco1")["H_info_isco"].first().sort_values().to_string())
print(f"\n  Δemp_ann distribution:\n{panel['delta_emp_ann'].describe()}")

print("\n[5/6] Cross-country regressions (3 specs)...")

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


y = panel["delta_emp_ann"].to_numpy()
ones = np.ones(len(panel))

# Spec 1: H_info only
X1 = np.column_stack([ones, panel["H_info_isco"].to_numpy()])
b1, se1, t1, p_two1, p_one1, r2_1 = ols(X1, y)
print(f"\n[Spec 1] delta_emp_ann ~ alpha + beta * H_info_ISCO")
print(f"  beta(H_info) = {b1[1]:+.4e}  SE {se1[1]:.4e}  t = {t1[1]:+.3f}  "
      f"p_two = {p_two1[1]:.4g}  p_one = {p_one1:.4g}")
print(f"  R^2 = {r2_1:.4f}")

# Spec 2: + country FE
country_dummies = pd.get_dummies(panel["geo"], prefix="cty",
                                 drop_first=True).astype(float)
X2 = np.column_stack([ones, panel["H_info_isco"].to_numpy(),
                      country_dummies.to_numpy()])
b2, se2, t2, p_two2, p_one2, r2_2 = ols(X2, y)
print(f"\n[Spec 2] + country FE (N countries = {panel['geo'].nunique()})")
print(f"  beta(H_info) = {b2[1]:+.4e}  SE {se2[1]:.4e}  t = {t2[1]:+.3f}  "
      f"p_one = {p_one2:.4g}")
print(f"  R^2 = {r2_2:.4f}")

# Spec 3: occupation within-transformation (de-mean by ISCO)
# (we cannot include occupation FE *and* H_info_ISCO since H_info_ISCO is
# collinear with ISCO. Within-occupation demean kills the H_info effect by
# construction, so this is not the right spec. Instead, use country FE only.)
print(f"\n  (Occupation FE is excluded because H_info_ISCO is at the "
      f"ISCO 1-digit level and would be perfectly collinear.)")

# Save
out = {
    "v2.6_CrossCountry": {
        "data": "Eurostat LFSA_EGAI2D, ISCO-08 1-digit, T sex, Y15-64",
        "N_panel": int(len(panel)),
        "n_countries": int(panel["geo"].nunique()),
        "n_isco_categories": int(panel["isco1"].nunique()),
        "H_info_mapping": H_INFO_ISCO,
        "spec_1_H_info_only": {
            "beta": float(b1[1]), "se": float(se1[1]), "t": float(t1[1]),
            "p_two": float(p_two1[1]), "p_one_positive": float(p_one1),
            "R2": float(r2_1),
        },
        "spec_2_country_FE": {
            "beta": float(b2[1]), "se": float(se2[1]), "t": float(t2[1]),
            "p_two": float(p_two2[1]), "p_one_positive": float(p_one2),
            "R2": float(r2_2),
        },
    },
}
with open(os.path.join(base, "v26_cross_country_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[6/6] Saved -> v26_cross_country_results.json")
