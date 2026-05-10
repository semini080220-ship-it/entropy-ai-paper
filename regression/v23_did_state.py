"""
v2.3 - DiD-style state-level identification.

  delta_emp_{i,s} = alpha + beta1 * H_info_RTI_i
                  + beta2 * AIstate_s
                  + beta3 * H_info_RTI_i x AIstate_s
                  + mu_i + nu_s + eps

  H4 prediction: beta3 > 0 (H_info effect is *stronger* in
  high-AI-adoption states; high-H_info occupations differentially
  preserved more in tech-intensive regions).

The state-level variation acts as a quasi-instrument: COVID, minimum
wage, and offshoring shocks affect all states (absorbed by state FE).
What varies between states is AI adoption intensity, which is
plausibly the causal channel for H4.

AI adoption proxy: state-level information-occupation share
  (Computer & Math occupations, SOC 15-1xxx + 15-2xxx) in 2019.
  This is a pre-period, occupation-mix-based proxy that is plausibly
  exogenous to 2019-2024 occupation-level employment changes.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
bls_24 = os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx")
bls_19 = os.path.join(base, "data/bls_2019/oesm19all/all_data_M_2019.xlsx")

print("[1/7] Loading BLS 2024 + 2019 (state-level slices, ~60s)...")
df24 = pd.read_excel(bls_24)
df24.columns = df24.columns.str.upper()
df19 = pd.read_excel(bls_19)
df19.columns = df19.columns.str.upper()

print(f"  2024 rows: {len(df24):,}, 2019 rows: {len(df19):,}")
print(f"  AREA_TYPE values: 2024={sorted(df24['AREA_TYPE'].dropna().unique())}, "
      f"2019={sorted(df19['AREA_TYPE'].dropna().unique())}")


def state_detailed(df, year):
    d = df.copy()
    # AREA_TYPE = 2 : state
    d = d[d["AREA_TYPE"] == 2]
    if "O_GROUP" in d.columns:
        d = d[d["O_GROUP"].astype(str).str.lower() == "detailed"]
    if "I_GROUP" in d.columns:
        d = d[d["I_GROUP"].astype(str).str.lower() == "cross-industry"]
    d["TOT_EMP"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["TOT_EMP", "OCC_CODE", "AREA_TITLE"])
    d = d[d["TOT_EMP"] > 0]
    return d[["AREA_TITLE", "OCC_CODE", "OCC_TITLE", "TOT_EMP"]].rename(
        columns={"TOT_EMP": f"emp_{year}"}
    )


print("\n[2/7] Filtering state-level detailed cross-industry rows...")
s24 = state_detailed(df24, 2024)
s19 = state_detailed(df19, 2019)
print(f"  2024 state-occupation cells: {len(s24):,}")
print(f"  2019 state-occupation cells: {len(s19):,}")
print(f"  unique states 2024: {s24['AREA_TITLE'].nunique()}")

# Merge on state + occupation
panel = pd.merge(s19, s24, on=["AREA_TITLE", "OCC_CODE"],
                 suffixes=("", "_24"))
panel["delta_emp_log"] = np.log(panel["emp_2024"] / panel["emp_2019"])
# Cap extreme outliers
panel["delta_emp_log"] = panel["delta_emp_log"].clip(-2, 2)
panel = panel.dropna(subset=["delta_emp_log"])
print(f"\n  Merged state x occupation panel: {len(panel):,}")
print(f"  delta_emp_log distribution: mean={panel['delta_emp_log'].mean():.4f}, "
      f"std={panel['delta_emp_log'].std():.4f}")

print("\n[3/7] Building AI-adoption proxy by state...")
# Tech occupations: SOC 15-1xxx (Computer) + 15-2xxx (Math)
s19["soc2"] = s19["OCC_CODE"].astype(str).str[:2]
s19["soc4"] = s19["OCC_CODE"].astype(str).str[:5]
tech_mask = s19["soc2"] == "15"
s19["tech_emp"] = np.where(tech_mask, s19["emp_2019"], 0)

state_tech = s19.groupby("AREA_TITLE").agg(
    total_emp_2019=("emp_2019", "sum"),
    tech_emp_2019=("tech_emp", "sum"),
).reset_index()
state_tech["tech_share"] = state_tech["tech_emp_2019"] / state_tech["total_emp_2019"]
state_tech["z_tech_share"] = stats.zscore(state_tech["tech_share"])
print(f"  State tech share distribution:")
print(state_tech.nlargest(5, "tech_share")[["AREA_TITLE", "tech_share"]].to_string(index=False))
print("  ---")
print(state_tech.nsmallest(5, "tech_share")[["AREA_TITLE", "tech_share"]].to_string(index=False))

print("\n[4/7] Joining panel with H_info (RTI) and AI-adoption proxy...")
v21 = pd.read_csv(os.path.join(base, "v21_main_data.csv"))
panel = panel.merge(v21[["OCC_CODE", "H_info_rti", "H_info_eloundou"]],
                    on="OCC_CODE", how="inner")
panel = panel.merge(state_tech[["AREA_TITLE", "tech_share", "z_tech_share"]],
                    on="AREA_TITLE", how="inner")
panel["z_H_info_rti"] = stats.zscore(panel["H_info_rti"])
panel["z_H_info_eloundou"] = stats.zscore(panel["H_info_eloundou"])
panel["interaction"] = panel["z_H_info_rti"] * panel["z_tech_share"]
panel["interaction_elo"] = panel["z_H_info_eloundou"] * panel["z_tech_share"]
print(f"  Final panel: N = {len(panel):,}")

print("\n[5/7] Spec 1: pooled OLS, no fixed effects")

def ols(X, y):
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    sigma2 = (res ** 2).sum() / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = b / se
    p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))
    r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, se, t, p_two, r2


y = panel["delta_emp_log"].to_numpy()
ones = np.ones(len(panel))

X1 = np.column_stack([
    ones,
    panel["z_H_info_rti"].to_numpy(),
    panel["z_tech_share"].to_numpy(),
    panel["interaction"].to_numpy(),
])
b1, se1, t1, p1, r2_1 = ols(X1, y)
labels1 = ["intercept", "z_H_info_RTI", "z_tech_share",
           "interaction (H_info_RTI x tech_share)"]
print(f"  N = {len(panel):,}")
for j, lab in enumerate(labels1):
    print(f"    {lab:42s}: b = {b1[j]:+.4e}  SE {se1[j]:.4e}  t = {t1[j]:+.3f}  p2 = {p1[j]:.4g}")
print(f"  R^2 = {r2_1:.4f}")
beta3_one = 1 - stats.t.cdf(t1[3], len(panel) - 4)
print(f"  H4 prediction: beta3 > 0  |  one-sided p = {beta3_one:.4g}")

print("\n[6/7] Spec 2: + occupation FE + state FE (two-way)")
# Use within-transformation (de-mean by occupation and by state)
panel["delta_demeaned"] = (panel["delta_emp_log"]
                            - panel.groupby("OCC_CODE")["delta_emp_log"].transform("mean")
                            - panel.groupby("AREA_TITLE")["delta_emp_log"].transform("mean")
                            + panel["delta_emp_log"].mean())
panel["interaction_demeaned"] = (panel["interaction"]
                                 - panel.groupby("OCC_CODE")["interaction"].transform("mean")
                                 - panel.groupby("AREA_TITLE")["interaction"].transform("mean")
                                 + panel["interaction"].mean())
# H_info_RTI is occupation-level so it's collinear with occupation FE.
# tech_share is state-level so it's collinear with state FE.
# Only the interaction survives.
y_dm = panel["delta_demeaned"].to_numpy()
X2 = np.column_stack([ones, panel["interaction_demeaned"].to_numpy()])
b2, se2, t2, p2, r2_2 = ols(X2, y_dm)
print(f"  Two-way FE (de-meaning), only interaction identified:")
print(f"    interaction (H_info_RTI x tech_share): "
      f"b = {b2[1]:+.4e}  SE {se2[1]:.4e}  t = {t2[1]:+.3f}  p2 = {p2[1]:.4g}")
print(f"  R^2 (within) = {r2_2:.4f}")
beta_did_one = 1 - stats.t.cdf(t2[1], len(panel) - 2)
print(f"  H4 prediction: beta_DiD > 0  |  one-sided p = {beta_did_one:.4g}")

print("\n[7/7] Spec 3 (robustness): same with Eloundou-based H_info instead of RTI")
panel["interaction_elo_demeaned"] = (panel["interaction_elo"]
                                     - panel.groupby("OCC_CODE")["interaction_elo"].transform("mean")
                                     - panel.groupby("AREA_TITLE")["interaction_elo"].transform("mean")
                                     + panel["interaction_elo"].mean())
X3 = np.column_stack([ones, panel["interaction_elo_demeaned"].to_numpy()])
b3, se3, t3, p3, r2_3 = ols(X3, y_dm)
print(f"    interaction (H_info_Eloundou x tech_share):")
print(f"    b = {b3[1]:+.4e}  SE {se3[1]:.4e}  t = {t3[1]:+.3f}  p2 = {p3[1]:.4g}")
beta_did_elo_one = 1 - stats.t.cdf(t3[1], len(panel) - 2)
print(f"  one-sided p = {beta_did_elo_one:.4g}")

# Save
results = {
    "v2.3_DiD": {
        "N_panel": int(len(panel)),
        "n_states": int(panel["AREA_TITLE"].nunique()),
        "n_occupations": int(panel["OCC_CODE"].nunique()),
        "ai_state_proxy": "tech_share = (Computer + Math occupations 2019) / total state employment 2019",
        "spec_1_pooled": {
            "beta1_H_info_RTI": float(b1[1]), "p1": float(p1[1]),
            "beta2_tech_share": float(b1[2]), "p2": float(p1[2]),
            "beta3_interaction": float(b1[3]),
            "p_two_beta3": float(p1[3]), "p_one_beta3": float(beta3_one),
            "R2": float(r2_1),
        },
        "spec_2_two_way_FE": {
            "beta_DiD": float(b2[1]),
            "se": float(se2[1]),
            "t": float(t2[1]),
            "p_two": float(p2[1]),
            "p_one_positive": float(beta_did_one),
            "R2_within": float(r2_2),
        },
        "spec_3_robustness_Eloundou": {
            "beta_DiD": float(b3[1]),
            "p_two": float(p3[1]),
            "p_one_positive": float(beta_did_elo_one),
        },
    },
}
with open(os.path.join(base, "v23_did_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved -> v23_did_results.json")
