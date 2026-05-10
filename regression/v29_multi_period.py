"""
v2.9 - Multi-period sliding-window analysis.

Run the same v2.7 ISCO 2-digit + country-FE specification on three
non-overlapping 5-year windows:
  Window 1: 2011 -> 2016 (early-2010s, pre-recovery / Eurozone crisis tail)
  Window 2: 2014 -> 2019 (mid-2010s, pre-ChatGPT)
  Window 3: 2019 -> 2024 (post-ChatGPT)

Plus an overlapping-mid window 2016 -> 2021 (mid-2010s through pandemic
shock) for additional resolution.

If H_info effect is monotonically increasing across windows -> AI is
accelerating a long-run gradient.
If only window 3 is large -> mostly AI-driven (post-2022 effect).
If window 1 is largest -> reverse causality / pre-existing trend.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
tsv = os.path.join(base, "data/eurostat_lfsa_egai2d.tsv")

print("[1/4] Parsing Eurostat panel...")
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


def panel_for_period(t0, t1, label):
    c0, c1 = year_cols[years.index(t0)], year_cols[years.index(t1)]
    p = df[["geo", "isco2", "H_info", c0, c1]].copy()
    p.columns = ["geo", "isco2", "H_info", "emp_t0", "emp_t1"]
    p = p.dropna(subset=["emp_t0", "emp_t1"])
    p = p[(p["emp_t0"] > 1) & (p["emp_t1"] > 1)]
    n_yrs = int(t1) - int(t0)
    p["delta_ann"] = (p["emp_t1"] / p["emp_t0"]) ** (1 / n_yrs) - 1
    return p


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


def fit(p, label):
    ones = np.ones(len(p))
    ctry_d = pd.get_dummies(p["geo"], prefix="cty",
                             drop_first=True).astype(float)
    X = np.column_stack([ones, p["H_info"].to_numpy(), ctry_d.to_numpy()])
    y = p["delta_ann"].to_numpy()
    b, se, t, p_two, p_one, r2 = ols(X, y)
    print(f"  {label:18s}  N = {len(p):,}  beta = {b[1]:+.4e}  "
          f"SE {se[1]:.4e}  t = {t[1]:+.3f}  p_one = {p_one:.4g}  R^2 = {r2:.4f}")
    return {"beta": float(b[1]), "se": float(se[1]),
            "t": float(t[1]), "p_one": float(p_one),
            "p_two": float(p_two[1]), "R2": float(r2),
            "N": int(len(p))}


print("\n[2/4] Sliding 5-year windows (country FE)...")
windows = [
    ("2011", "2016", "W1: 2011-2016"),
    ("2014", "2019", "W2: 2014-2019"),
    ("2016", "2021", "W3: 2016-2021"),
    ("2019", "2024", "W4: 2019-2024"),
]
results = {}
for t0, t1, lab in windows:
    p = panel_for_period(t0, t1, lab)
    if len(p) < 100:
        print(f"  {lab}: too few rows ({len(p)}), skipping")
        continue
    results[lab] = fit(p, lab)

print("\n[3/4] Trend test: monotonically increasing beta over time?")
betas = [(lab, r["beta"], r["t"]) for lab, r in results.items()]
print(f"  Window         beta             t      delta_beta from W1")
b1 = betas[0][1] if betas else 0.0
for lab, b, t in betas:
    print(f"  {lab:18s}  {b:+.4e}   {t:+6.2f}    {b - b1:+.4e}")

if len(betas) >= 2:
    monotone = all(betas[i][1] <= betas[i+1][1] for i in range(len(betas)-1))
    print(f"\n  Monotonically increasing: {monotone}")

# Stacked panel with window dummies
print("\n[4/4] Stacked panel with window FE + (H_info x window) interactions")
stacked_parts = []
for t0, t1, lab in windows:
    p = panel_for_period(t0, t1, lab)
    if len(p) < 100:
        continue
    p["window"] = lab
    stacked_parts.append(p[["geo", "isco2", "H_info", "delta_ann", "window"]])
stacked = pd.concat(stacked_parts, ignore_index=True)
print(f"  stacked N = {len(stacked):,}, windows = {stacked['window'].nunique()}")

# Window dummies (drop W1 as baseline)
window_d = pd.get_dummies(stacked["window"], prefix="w",
                           drop_first=True).astype(float)
ctry_d = pd.get_dummies(stacked["geo"], prefix="cty",
                         drop_first=True).astype(float)

# H_info interactions with each window dummy
hinfo = stacked["H_info"].to_numpy()
interactions = window_d.multiply(hinfo, axis=0)
interactions.columns = [f"int_{c}" for c in interactions.columns]

X = np.column_stack([
    np.ones(len(stacked)),
    hinfo,
    window_d.to_numpy(),
    interactions.to_numpy(),
    ctry_d.to_numpy(),
])
y = stacked["delta_ann"].to_numpy()
n, k = X.shape
b, *_ = np.linalg.lstsq(X, y, rcond=None)
res = y - X @ b
sigma2 = (res ** 2).sum() / (n - k)
cov = sigma2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
t = b / se
p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))

print(f"  Stacked OLS results (W1 = baseline):")
print(f"    beta(H_info | W1)         = {b[1]:+.4e}  t = {t[1]:+.3f}  p2 = {p_two[1]:.4g}")
window_names = list(window_d.columns)
n_windows = len(window_names)
for j in range(n_windows):
    idx_int = 1 + 1 + n_windows + j  # intercept + H_info + window dummies + interactions
    p_one_j = 1 - stats.t.cdf(t[idx_int], n - k)
    print(f"    H_info x {window_names[j]:20s} = {b[idx_int]:+.4e}  "
          f"t = {t[idx_int]:+.3f}  p_one = {p_one_j:.4g}")

# Save
out = {
    "v2.9_multi_period": {
        "windows": {lab: r for lab, r in results.items()},
        "monotone_increasing": (
            all(betas[i][1] <= betas[i+1][1] for i in range(len(betas)-1))
            if len(betas) >= 2 else None
        ),
        "stacked_baseline_beta": float(b[1]),
        "stacked_window_interactions": {
            window_names[j]: {
                "beta_int": float(b[1 + 1 + n_windows + j]),
                "t": float(t[1 + 1 + n_windows + j]),
                "p_two": float(p_two[1 + 1 + n_windows + j]),
                "p_one_positive": float(1 - stats.t.cdf(t[1 + 1 + n_windows + j], n - k)),
            } for j in range(n_windows)
        },
    },
}
with open(os.path.join(base, "v29_multi_period_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n  Saved -> v29_multi_period_results.json")
