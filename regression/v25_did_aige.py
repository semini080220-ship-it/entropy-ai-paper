"""
v2.5 - DiD with Felten AIGE (AI Geographic Exposure) as state-level
       AI-adoption proxy. Felten et al. (2021, SMJ) AIGE is a published
       academic measure derived independently of BLS occupation data,
       so it is a more defensible state-level instrument than the
       v2.3-v2.4 tech-occupation share.

  H4-info-mediated-by-AI prediction:
    DiD interaction (H_info_RTI x AIGE_state) > 0.

  Plus sub-sample comparison: H_info effect in high-AIGE vs low-AIGE
  states (parallel to v2.4 split, now with academic-grade AI proxy).
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
bls_19 = os.path.join(base, "data/bls_2019/oesm19all/all_data_M_2019.xlsx")
bls_24 = os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx")
felten = os.path.join(base, "data/felten_aioe.xlsx")

print("[1/6] Loading state-level AIGE from Felten Appendix C...")
aige = pd.read_excel(felten, sheet_name="Appendix C")
# State-level rows have FIPS Code ending in '000' (state FIPS code * 1000).
state_aige = aige[aige["FIPS Code"] % 1000 == 0].copy()
state_aige = state_aige[~state_aige["Geographic Area"].astype(str).str.contains(
    "United States", case=False, na=False)]
state_aige.columns = ["fips", "AREA_TITLE", "AIGE"]
state_aige["z_AIGE"] = stats.zscore(state_aige["AIGE"])
print(f"  N states with AIGE: {len(state_aige)}")
print(f"\n  Top 5 by AIGE (most AI-exposed states):")
print(state_aige.nlargest(5, "AIGE")[["AREA_TITLE", "AIGE"]].to_string(index=False))
print("  ---")
print(state_aige.nsmallest(5, "AIGE")[["AREA_TITLE", "AIGE"]].to_string(index=False))

print("\n[2/6] Loading BLS 2019 + 2024 state-level panel...")
df19 = pd.read_excel(bls_19); df19.columns = df19.columns.str.upper()
df24 = pd.read_excel(bls_24); df24.columns = df24.columns.str.upper()


def state_detailed(df, year):
    d = df[(df["AREA_TYPE"] == 2)
           & (df["O_GROUP"].astype(str).str.lower() == "detailed")
           & (df["I_GROUP"].astype(str).str.lower() == "cross-industry")].copy()
    d["TOT_EMP"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["TOT_EMP", "OCC_CODE", "AREA_TITLE"])
    d = d[d["TOT_EMP"] > 0]
    return d[["AREA_TITLE", "OCC_CODE", "TOT_EMP"]].rename(
        columns={"TOT_EMP": f"emp_{year}"}
    )


s19 = state_detailed(df19, 2019)
s24 = state_detailed(df24, 2024)
panel = s19.merge(s24, on=["AREA_TITLE", "OCC_CODE"])
panel["delta_emp_log"] = np.log(panel["emp_2024"] / panel["emp_2019"]).clip(-2, 2)
panel = panel.dropna(subset=["delta_emp_log"])

# Merge with AIGE (state) and H_info_RTI (occupation)
v21 = pd.read_csv(os.path.join(base, "v21_main_data.csv"))
panel = panel.merge(v21[["OCC_CODE", "H_info_rti", "H_info_eloundou"]],
                    on="OCC_CODE")
panel = panel.merge(state_aige[["AREA_TITLE", "AIGE", "z_AIGE"]],
                    on="AREA_TITLE", how="inner")
panel["z_H_info_rti"] = stats.zscore(panel["H_info_rti"])
print(f"\n[3/6] Merged panel: N = {len(panel):,}, "
      f"states = {panel['AREA_TITLE'].nunique()}")

print("\n[4/6] DiD with Felten AIGE (two-way FE)...")
panel["interaction"] = panel["z_H_info_rti"] * panel["z_AIGE"]
panel["dy_dm"] = (panel["delta_emp_log"]
                  - panel.groupby("OCC_CODE")["delta_emp_log"].transform("mean")
                  - panel.groupby("AREA_TITLE")["delta_emp_log"].transform("mean")
                  + panel["delta_emp_log"].mean())
panel["int_dm"] = (panel["interaction"]
                   - panel.groupby("OCC_CODE")["interaction"].transform("mean")
                   - panel.groupby("AREA_TITLE")["interaction"].transform("mean")
                   + panel["interaction"].mean())

X = np.column_stack([np.ones(len(panel)), panel["int_dm"].to_numpy()])
y = panel["dy_dm"].to_numpy()
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
print(f"  beta_DiD (H_info_RTI x AIGE) = {b[1]:+.4e}  SE {se[1]:.4e}")
print(f"  t = {t[1]:+.3f}  p_two = {p_two[1]:.4g}  p_one (b>0) = {p_one:.4g}")
print(f"  R^2 (within) = {r2:.4f}")

print("\n[5/6] Sub-sample analysis: H_info effect in high-AIGE vs low-AIGE states")
state_aige["high_aige"] = (state_aige["AIGE"] >= state_aige["AIGE"].median()).astype(int)
panel = panel.merge(state_aige[["AREA_TITLE", "high_aige"]], on="AREA_TITLE")


def occ_h_info_effect(p, label):
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


r_hi = occ_h_info_effect(panel[panel["high_aige"] == 1], "High-AIGE states")
r_lo = occ_h_info_effect(panel[panel["high_aige"] == 0], "Low-AIGE states ")
diff = r_hi["beta"] - r_lo["beta"]
diff_se = np.sqrt(r_hi["se"]**2 + r_lo["se"]**2)
diff_t = diff / diff_se
diff_p_one = 1 - stats.t.cdf(diff_t, r_hi["N"] + r_lo["N"] - 4)
print(f"\n  Difference (high - low) = {diff:+.4e}, SE = {diff_se:.4e}")
print(f"  t = {diff_t:+.3f}, one-sided p = {diff_p_one:.4g}")

print("\n[6/6] Robustness: Tertile split (top 17 / mid 17 / bottom 17 states)")
state_aige["tertile"] = pd.qcut(state_aige["AIGE"], 3, labels=["bottom", "mid", "top"])
panel = panel.merge(state_aige[["AREA_TITLE", "tertile"]], on="AREA_TITLE")
for t_name in ["bottom", "mid", "top"]:
    sub = panel[panel["tertile"] == t_name]
    if len(sub) > 100:
        occ_h_info_effect(sub, f"{t_name:6s} AIGE tertile")

# Save
out = {
    "v2.5_DiD_AIGE": {
        "N_panel": int(len(panel)),
        "n_states": int(panel["AREA_TITLE"].nunique()),
        "Felten_AIGE": "from data/felten_aioe.xlsx Appendix C, state-level",
        "DiD_two_way_FE": {
            "beta": float(b[1]), "se": float(se[1]),
            "t": float(t[1]), "p_two": float(p_two[1]),
            "p_one_positive": float(p_one), "R2_within": float(r2),
        },
        "subsample_split": {
            "high_AIGE": r_hi, "low_AIGE": r_lo,
            "difference": float(diff), "diff_t": float(diff_t),
            "diff_p_one": float(diff_p_one),
        },
    },
}
with open(os.path.join(base, "v25_did_aige_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved -> v25_did_aige_results.json")
