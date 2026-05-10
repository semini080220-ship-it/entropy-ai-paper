"""
Phase B regression: full BLS occupational panel x O*NET multi-element
physical demand index.

Steps:
  1. Load BLS OEWS 2019 + 2024 national-level data
  2. Filter to detailed occupations (O_GROUP=='detailed') and cross-industry
  3. Compute annualised employment growth 2019->2024 (5-year)
  4. Load O*NET Work Context (sitting/standing/walking time, scale CT 1-5)
  5. Build composite physical_index = -sitting + standing + walking
  6. Map to MET in [1.5, 5.0] -> E^human (J/h, 70 kg body)
  7. Merge BLS x O*NET on SOC code
  8. OLS: delta_emp ~ alpha + beta * E^human
  9. Save results JSON
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
bls_24 = os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx")
bls_19 = os.path.join(base, "data/bls_2019/oesm19all/all_data_M_2019.xlsx")
onet = os.path.join(base, "data/onet/db_30_2_excel")

print("=" * 64)
print("Phase B regression -- full BLS panel x O*NET multi-element")
print("=" * 64)

print("\n[1/8] Loading BLS 2024 (~30s)...")
df24 = pd.read_excel(bls_24)
df24.columns = df24.columns.str.upper()
print(f"  rows: {len(df24):,}, columns sample: {df24.columns.tolist()[:12]}")

print("\n[2/8] Loading BLS 2019 (~30s)...")
df19 = pd.read_excel(bls_19)
df19.columns = df19.columns.str.upper()
print(f"  rows: {len(df19):,}, columns sample: {df19.columns.tolist()[:12]}")


def national_detailed(df, year):
    d = df.copy()
    if "AREA_TYPE" in d.columns:
        d = d[d["AREA_TYPE"] == 1]
    if "O_GROUP" in d.columns:
        d = d[d["O_GROUP"].astype(str).str.lower() == "detailed"]
    if "I_GROUP" in d.columns:
        d = d[d["I_GROUP"].astype(str).str.lower() == "cross-industry"]
    d["TOT_EMP"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["TOT_EMP", "OCC_CODE"])
    d = d[d["TOT_EMP"] > 0]
    return d[["OCC_CODE", "OCC_TITLE", "TOT_EMP"]].rename(
        columns={"TOT_EMP": f"emp_{year}", "OCC_TITLE": f"title_{year}"}
    )


print("\n[3/8] Filtering national detailed cross-industry rows...")
n24 = national_detailed(df24, 2024)
n19 = national_detailed(df19, 2019)
print(f"  2024 national-detailed: {len(n24):,}")
print(f"  2019 national-detailed: {len(n19):,}")

m = pd.merge(n19, n24, on="OCC_CODE")
m["delta_emp_ann"] = (m["emp_2024"] / m["emp_2019"]) ** (1 / 5) - 1
m["delta_emp_ann"] = m["delta_emp_ann"].replace([np.inf, -np.inf], np.nan)
m = m.dropna(subset=["delta_emp_ann"])
print(f"  merged + growth: {len(m):,} occupations")
print(f"  delta_emp_ann distribution:\n{m['delta_emp_ann'].describe()}")

print("\n[4/8] Loading O*NET Work Context...")
wc = pd.read_excel(os.path.join(onet, "Work Context.xlsx"))
print(f"  rows: {len(wc):,}")
print(f"  Scale IDs: {sorted(wc['Scale ID'].dropna().unique().tolist())}")

elements = {
    "4.C.2.d.1.a": "sitting",
    "4.C.2.d.1.b": "standing",
    "4.C.2.d.1.d": "walking",
}

print("\n[5/8] Extracting physical activity time (CT scale, 1-5)...")
phys = {}
for eid, name in elements.items():
    sub = wc[(wc["Element ID"] == eid) & (wc["Scale ID"] == "CT")].copy()
    if len(sub) == 0:
        # fallback to CTP or CXP
        for alt in ["CTP", "CX", "CXP"]:
            sub = wc[(wc["Element ID"] == eid) & (wc["Scale ID"] == alt)].copy()
            if len(sub) > 0:
                print(f"  {eid} ({name}): using scale {alt}")
                break
    if len(sub) == 0:
        print(f"  {eid} ({name}): NOT FOUND, skipping")
        continue
    sub["soc"] = sub["O*NET-SOC Code"].astype(str).str[:7]
    avg = sub.groupby("soc")["Data Value"].mean().reset_index()
    avg.columns = ["soc", name]
    phys[name] = avg
    print(f"  {eid} ({name}): {len(avg)} SOCs, "
          f"mean={avg[name].mean():.2f} range=[{avg[name].min():.2f}, {avg[name].max():.2f}]")

print("\n[6/8] Building composite physical_index and E^human...")
if not all(k in phys for k in ("sitting", "standing", "walking")):
    raise RuntimeError("Missing one of sitting/standing/walking; check scales")

c = phys["sitting"].merge(phys["standing"], on="soc").merge(phys["walking"], on="soc")
c["phys_index"] = -c["sitting"] + c["standing"] + c["walking"]
mn, mx = c["phys_index"].min(), c["phys_index"].max()
c["MET"] = 1.5 + (c["phys_index"] - mn) / (mx - mn) * 3.5
c["E_human"] = c["MET"] * 70.0 * 4184.0
print(f"  composite phys_index range: [{mn:.2f}, {mx:.2f}]")
print(f"  E_human (J/h) summary:\n{c['E_human'].describe()}")

# top/bottom for sanity check
sn = c.merge(m[["OCC_CODE", "title_2024"]], left_on="soc", right_on="OCC_CODE", how="left")
print("\n  Top 5 most physical (highest E^human):")
print(sn.nlargest(5, "E_human")[["soc", "title_2024", "sitting", "standing", "walking", "E_human"]].to_string(index=False))
print("\n  Bottom 5 most sedentary (lowest E^human):")
print(sn.nsmallest(5, "E_human")[["soc", "title_2024", "sitting", "standing", "walking", "E_human"]].to_string(index=False))

print("\n[7/8] Merging BLS x O*NET...")
final = pd.merge(m, c, left_on="OCC_CODE", right_on="soc")
print(f"  final merged sample: N = {len(final):,}")

print("\n[8/8] OLS regression: delta_emp_ann ~ alpha + beta * E^human")
X = np.column_stack([np.ones(len(final)), final["E_human"].values])
y = final["delta_emp_ann"].values
b, *_ = np.linalg.lstsq(X, y, rcond=None)
alpha, slope = b
res = y - X @ b
n, k = X.shape
sigma2 = (res ** 2).sum() / (n - k)
cov = sigma2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
t_stat = b / se
p_two = 2 * (1 - stats.t.cdf(np.abs(t_stat), n - k))
p_one = 1 - stats.t.cdf(t_stat[1], n - k)
r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
r_p, p_p = stats.pearsonr(final["E_human"].values, y)
r_s, p_s = stats.spearmanr(final["E_human"].values, y)

print()
print("=" * 64)
print(f"Phase B result (N = {n})")
print("=" * 64)
print(f"  alpha (intercept)       : {alpha:+.6f}   SE {se[0]:.6f}")
print(f"  beta  (slope, E^human)  : {slope:+.4e}   SE {se[1]:.4e}")
print(f"  t-statistic on beta     : {t_stat[1]:+.3f}")
print(f"  p (two-sided)           : {p_two[1]:.4g}")
print(f"  p (one-sided, H4: b>0)  : {p_one:.4g}")
print(f"  R^2                     : {r2:.4f}")
print()
print(f"  Pearson  r              : {r_p:+.4f}  (p = {p_p:.4g})")
print(f"  Spearman rho            : {r_s:+.4f}  (p = {p_s:.4g})")

if slope > 0 and p_one < 0.001:
    v = f"H4 STRONGLY CONFIRMED on full panel (N={n}): beta>0, one-sided p={p_one:.2e}"
elif slope > 0 and p_one < 0.05:
    v = f"H4 CONFIRMED on full panel (N={n}): beta>0, one-sided p={p_one:.4f}"
elif slope > 0 and p_one < 0.10:
    v = f"H4 marginal: beta>0, one-sided p={p_one:.4f}"
elif slope > 0:
    v = f"H4 sign correct (beta>0) but not significant: p={p_one:.4f}"
else:
    v = f"H4 REJECTED: beta={slope:+.4e} < 0"
print(f"\nVerdict: {v}")

# Save
out = {
    "phase": "B_full_BLS",
    "N": int(n),
    "alpha": float(alpha),
    "se_alpha": float(se[0]),
    "beta": float(slope),
    "se_beta": float(se[1]),
    "t_beta": float(t_stat[1]),
    "p_two_sided": float(p_two[1]),
    "p_one_sided_positive": float(p_one),
    "R_squared": float(r2),
    "pearson_r": float(r_p),
    "pearson_p": float(p_p),
    "spearman_rho": float(r_s),
    "spearman_p": float(p_s),
    "verdict": v,
    "delta_emp_describe": m["delta_emp_ann"].describe().to_dict(),
    "phys_index_range": {"min": float(mn), "max": float(mx)},
}
out_path = os.path.join(base, "phase_b_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(f"\nResults JSON -> {out_path}")

# also save final dataframe for paper table
final_out = os.path.join(base, "phase_b_final.csv")
final[["OCC_CODE", "title_2024", "emp_2019", "emp_2024", "delta_emp_ann",
       "sitting", "standing", "walking", "phys_index", "MET", "E_human"]].to_csv(
    final_out, index=False
)
print(f"Final dataframe -> {final_out}")
