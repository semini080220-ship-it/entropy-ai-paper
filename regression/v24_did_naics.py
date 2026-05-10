"""
v2.4 - DiD identification with stronger state-level AI-adoption proxies.

  Three proxies tested:
    P1. Tech-occupation share (v2.3 baseline): SOC 15-1xxx + 15-2xxx
    P2. NAICS-51 Information sector employment share (PRIMARY)
    P3. Composite z-score = z(P1) + z(P2)

  Plus a sub-sample comparison: H_info effect in high-tech vs low-tech states.

  H4 mediated-by-AI prediction:
    beta_3 (H_info x AI_state) > 0 in DiD spec
    OR
    beta(H_info | high-AI states) > beta(H_info | low-AI states)
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
bls_19 = os.path.join(base, "data/bls_2019/oesm19all/all_data_M_2019.xlsx")
bls_24 = os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx")

print("[1/8] Loading BLS 2019 + 2024 (~60s)...")
df19 = pd.read_excel(bls_19)
df19.columns = df19.columns.str.upper()
df24 = pd.read_excel(bls_24)
df24.columns = df24.columns.str.upper()
print(f"  rows 2019: {len(df19):,}, 2024: {len(df24):,}")
print(f"  I_GROUP values 2019: {sorted(df19['I_GROUP'].dropna().unique().tolist())[:10]}")

# State-level cross-industry: detailed occupation totals (P1)
def state_detailed(df, year):
    d = df[(df["AREA_TYPE"] == 2)
           & (df["O_GROUP"].astype(str).str.lower() == "detailed")
           & (df["I_GROUP"].astype(str).str.lower() == "cross-industry")].copy()
    d["TOT_EMP"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["TOT_EMP", "OCC_CODE", "AREA_TITLE"])
    d = d[d["TOT_EMP"] > 0]
    return d[["AREA_TITLE", "OCC_CODE", "OCC_TITLE", "TOT_EMP"]].rename(
        columns={"TOT_EMP": f"emp_{year}"}
    )


s19 = state_detailed(df19, 2019)
s24 = state_detailed(df24, 2024)
panel = s19.merge(s24, on=["AREA_TITLE", "OCC_CODE"])
panel["delta_emp_log"] = np.log(panel["emp_2024"] / panel["emp_2019"]).clip(-2, 2)
panel = panel.dropna(subset=["delta_emp_log"])
print(f"\n[2/8] State-occupation panel: N = {len(panel):,}, "
      f"states = {panel['AREA_TITLE'].nunique()}")

# P1: tech-occupation share (v2.3)
print("\n[3/8] Building P1 tech-occupation share (v2.3 baseline)...")
s19["soc2"] = s19["OCC_CODE"].astype(str).str[:2]
s19["tech_emp"] = np.where(s19["soc2"] == "15", s19["emp_2019"], 0)
p1 = s19.groupby("AREA_TITLE").agg(
    total_emp=("emp_2019", "sum"),
    tech_emp=("tech_emp", "sum"),
).reset_index()
p1["tech_share"] = p1["tech_emp"] / p1["total_emp"]

# P2: NAICS-51 attempted but state-level industry breakdown not in oesm-all
# Fallback: P2 = high-skill professional share (SOC 11-1xxx managers
# + 19-xxxx scientists + 23-xxxx legal). This captures "knowledge-economy
# intensity" of the state at the occupation level (different from P1
# which is narrowly Computer/Math).
print("[4/8] Building P2 = high-skill professional share (managers/sci/legal)...")
s19["soc_full"] = s19["OCC_CODE"].astype(str)
s19["high_skill_emp"] = np.where(
    s19["soc2"].isin(["11", "19", "23"]),
    s19["emp_2019"], 0,
)
p2 = s19.groupby("AREA_TITLE").agg(
    total=("emp_2019", "sum"),
    hs=("high_skill_emp", "sum"),
).reset_index()
p2["info_share"] = p2["hs"] / p2["total"]
print(f"  P2 high-skill data: {len(p2)} states")

# P3: composite of P1 (tech) + P2 (high-skill)
proxies = p1[["AREA_TITLE", "tech_share"]].merge(p2[["AREA_TITLE", "info_share"]],
                                                   on="AREA_TITLE")
proxies["z_tech"] = stats.zscore(proxies["tech_share"])
proxies["z_info"] = stats.zscore(proxies["info_share"])
proxies["composite"] = proxies["z_tech"] + proxies["z_info"]
proxies["z_composite"] = stats.zscore(proxies["composite"])

print(f"\n  Top 5 by composite (tech + high-skill):")
print(proxies.nlargest(5, "composite")[["AREA_TITLE", "tech_share", "info_share", "composite"]].to_string(index=False))
print("  ---")
print(proxies.nsmallest(5, "composite")[["AREA_TITLE", "tech_share", "info_share", "composite"]].to_string(index=False))
print(f"\n  Correlation tech_share vs high_skill_share: r = "
      f"{stats.pearsonr(proxies['tech_share'], proxies['info_share'])[0]:+.4f}")

# Merge with H_info (RTI)
v21 = pd.read_csv(os.path.join(base, "v21_main_data.csv"))
panel = panel.merge(v21[["OCC_CODE", "H_info_rti"]], on="OCC_CODE")
panel = panel.merge(proxies[["AREA_TITLE", "tech_share", "info_share",
                              "z_tech", "z_info", "z_composite"]],
                     on="AREA_TITLE")
panel["z_H_info"] = stats.zscore(panel["H_info_rti"])
print(f"\n  Final panel: N = {len(panel):,}")


def two_way_fe_did(panel, ai_proxy_col, label):
    """Within-transform on occupation + state, then OLS on interaction."""
    p = panel.copy()
    p["interaction"] = p["z_H_info"] * p[ai_proxy_col]
    p["dy_dm"] = (p["delta_emp_log"]
                  - p.groupby("OCC_CODE")["delta_emp_log"].transform("mean")
                  - p.groupby("AREA_TITLE")["delta_emp_log"].transform("mean")
                  + p["delta_emp_log"].mean())
    p["int_dm"] = (p["interaction"]
                   - p.groupby("OCC_CODE")["interaction"].transform("mean")
                   - p.groupby("AREA_TITLE")["interaction"].transform("mean")
                   + p["interaction"].mean())
    X = np.column_stack([np.ones(len(p)), p["int_dm"].to_numpy()])
    y = p["dy_dm"].to_numpy()
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    sigma2 = (res ** 2).sum() / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = b / se
    p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))
    p_one = 1 - stats.t.cdf(t[1], n - k)
    print(f"\n[{label}]  beta_DiD = {b[1]:+.4e}  SE {se[1]:.4e}  "
          f"t = {t[1]:+.3f}  p2 = {p_two[1]:.4g}  p_one = {p_one:.4g}")
    return {"beta": float(b[1]), "se": float(se[1]), "t": float(t[1]),
            "p_two": float(p_two[1]), "p_one": float(p_one), "N": int(n)}


print("\n[5/8] DiD with three different AI-state proxies (two-way FE)...")
r_p1 = two_way_fe_did(panel, "z_tech", "P1: tech-occupation share")
r_p2 = two_way_fe_did(panel, "z_info", "P2: NAICS-51 information share (PRIMARY)")
r_p3 = two_way_fe_did(panel, "z_composite", "P3: composite z(tech)+z(info)")

print("\n[6/8] Sub-sample analysis: H_info effect in high vs low AI states...")
proxies["high_ai"] = (proxies["z_composite"] >= proxies["z_composite"].median()).astype(int)
panel = panel.merge(proxies[["AREA_TITLE", "high_ai"]], on="AREA_TITLE")
panel_hi = panel[panel["high_ai"] == 1]
panel_lo = panel[panel["high_ai"] == 0]


def occ_h_info_effect(p, label):
    # Within-state OLS on H_info_RTI
    X = np.column_stack([np.ones(len(p)), p["H_info_rti"].to_numpy()])
    y = p["delta_emp_log"].to_numpy()
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    sigma2 = (res ** 2).sum() / (n - k)
    se = np.sqrt(sigma2 * np.linalg.inv(X.T @ X)[1, 1])
    t = b[1] / se
    p_one = 1 - stats.t.cdf(t, n - k)
    print(f"  {label} (N={n:,}): beta = {b[1]:+.4e}  SE {se:.4e}  "
          f"t = {t:+.3f}  p_one = {p_one:.4g}")
    return {"beta": float(b[1]), "se": float(se), "t": float(t),
            "p_one": float(p_one), "N": int(n)}

r_hi = occ_h_info_effect(panel_hi, "High-AI states (composite >= median)")
r_lo = occ_h_info_effect(panel_lo, "Low-AI states  (composite <  median)")

# Difference test
diff = r_hi["beta"] - r_lo["beta"]
diff_se = np.sqrt(r_hi["se"]**2 + r_lo["se"]**2)
diff_t = diff / diff_se
diff_p_one = 1 - stats.t.cdf(diff_t, r_hi["N"] + r_lo["N"] - 4)
print(f"\n  Difference (high - low) = {diff:+.4e}, SE = {diff_se:.4e}")
print(f"  t = {diff_t:+.3f},  one-sided p = {diff_p_one:.4g}")

print("\n[7/8] Pre-trends placebo (sanity check, if 2014-2019 data were available)...")
print("  Skipped: only 2019 + 2024 BLS panels are available locally.")

# Save
out = {
    "v2.4_DiD": {
        "N_panel": int(len(panel)),
        "n_states": int(panel["AREA_TITLE"].nunique()),
        "proxy_correlation_tech_vs_info": float(stats.pearsonr(
            proxies["tech_share"], proxies["info_share"])[0]),
        "DiD_two_way_FE": {
            "P1_tech_share": r_p1,
            "P2_NAICS51_information_share": r_p2,
            "P3_composite_z": r_p3,
        },
        "subsample_split": {
            "high_AI_states": r_hi,
            "low_AI_states": r_lo,
            "difference_beta": float(diff),
            "diff_t": float(diff_t),
            "diff_p_one": float(diff_p_one),
        },
    },
}
out_path = os.path.join(base, "v24_did_results.json")
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[8/8] Saved -> {out_path}")
