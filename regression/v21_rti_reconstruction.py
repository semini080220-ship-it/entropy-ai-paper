"""
v2.1 - Reconstruct Routine Task Intensity (RTI) from O*NET 30.2
       in the Acemoglu-Autor (2011) tradition. RTI is methodologically
       INDEPENDENT of any AI-exposure measure (it uses occupation task
       importance, not LLM substitutability).

  RTI_i = (1/2)[z(R_cognitive) + z(R_manual)]
        - (1/3)[z(NR_analytic) + z(NR_interactive) + z(NR_manual)]

  H_info_RTI = -RTI  (higher = more non-routine = higher info entropy)

This breaks the tautology: H_info_RTI is independent of Eloundou alpha,
which is what the Gemini critique flagged as the paper's #1 weakness.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
onet = os.path.join(base, "data/onet/db_30_2_excel")

print("[1/6] Loading O*NET Work Activities + base panels...")
wa = pd.read_excel(os.path.join(onet, "Work Activities.xlsx"))
final = pd.read_csv(os.path.join(base, "phase_b_final.csv"))
final = final.rename(columns={"E_human": "E_thermo_v1"})

elo = pd.read_csv(os.path.join(base, "data/eloundou_occ_level.csv"))
elo["soc"] = elo["O*NET-SOC Code"].astype(str).str[:7]
elo_agg = elo.groupby("soc")[["dv_rating_alpha", "dv_rating_gamma"]].mean().reset_index()
elo_agg["H_info_eloundou"] = 1.0 - elo_agg["dv_rating_alpha"]

# RTI 5-category mapping (Acemoglu-Autor 2011 inspired)
RTI_MAP = {
    "R_cog": [
        "4.A.2.a.3",  # Evaluating Info to Determine Compliance
        "4.A.4.c.1",  # Performing Administrative Activities
        "4.A.3.b.6",  # Documenting/Recording Information
    ],
    "R_man": [
        "4.A.3.a.3",  # Controlling Machines and Processes
        "4.A.3.a.2",  # Handling and Moving Objects
        "4.A.3.a.1",  # Performing General Physical Activities
    ],
    "NR_anal": [
        "4.A.2.a.4",  # Analyzing Data or Information
        "4.A.2.b.2",  # Thinking Creatively
        "4.A.2.b.4",  # Developing Objectives and Strategies
    ],
    "NR_int": [
        "4.A.4.a.4",  # Establishing/Maintaining Interpersonal Relationships
        "4.A.4.b.4",  # Guiding, Directing, Motivating Subordinates
        "4.A.4.b.5",  # Coaching and Developing Others
    ],
    "NR_man": [
        "4.A.3.a.4",  # Operating Vehicles/Mechanized Devices/Equipment
        "4.A.3.b.4",  # Repairing/Maintaining Mechanical Equipment
        "4.A.3.b.5",  # Repairing/Maintaining Electronic Equipment
    ],
}

print("\n[2/6] Building RTI 5-category scores (Importance scale)...")
def category_score(elems, scale="IM"):
    sub = wa[(wa["Element ID"].isin(elems)) & (wa["Scale ID"] == scale)].copy()
    sub["soc"] = sub["O*NET-SOC Code"].astype(str).str[:7]
    return sub.groupby("soc")["Data Value"].mean()

cats = {name: category_score(elems) for name, elems in RTI_MAP.items()}
df = pd.DataFrame(cats).dropna()
print(f"  N SOC codes with all 5 categories: {len(df)}")
for c in df.columns:
    print(f"    {c:8s}: mean={df[c].mean():.2f}, range=[{df[c].min():.2f}, {df[c].max():.2f}]")

print("\n[3/6] Computing RTI...")
for c in df.columns:
    df[f"z_{c}"] = stats.zscore(df[c])
df["RTI"] = 0.5 * (df["z_R_cog"] + df["z_R_man"]) - \
            (1/3) * (df["z_NR_anal"] + df["z_NR_int"] + df["z_NR_man"])
df["H_info_rti"] = -df["RTI"]
df = df.reset_index()

# Top/bottom by RTI for sanity check
title_lookup = final[["OCC_CODE", "title_2024"]].drop_duplicates(subset="OCC_CODE")
df_t = df.merge(title_lookup, left_on="soc", right_on="OCC_CODE", how="left")

print("\n  Top 5 RTI (most routine, expected: clerical/repetitive):")
top = df_t.nlargest(5, "RTI")[["soc", "title_2024", "RTI", "R_cog", "R_man", "NR_anal"]]
print(top.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n  Bottom 5 RTI (most non-routine, expected: managerial/creative):")
bot = df_t.nsmallest(5, "RTI")[["soc", "title_2024", "RTI", "R_cog", "R_man", "NR_anal"]]
print(bot.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n[4/6] Merging with BLS panel + Eloundou for regression...")
m = final.merge(elo_agg, left_on="OCC_CODE", right_on="soc", how="inner")
m = m.drop(columns=["soc"])
m = m.merge(df[["soc", "RTI", "H_info_rti"]], left_on="OCC_CODE",
            right_on="soc", how="inner").drop(columns=["soc"])
print(f"  Final regression sample: N = {len(m)}")

# Tautology check: how independent is RTI from Eloundou alpha?
r_proxy, p_proxy = stats.pearsonr(m["H_info_rti"].to_numpy(),
                                   m["H_info_eloundou"].to_numpy())
print(f"\n  *** TAUTOLOGY CHECK ***")
print(f"  Pearson r(H_info_RTI, H_info_Eloundou) = {r_proxy:+.4f}, p = {p_proxy:.4g}")
print(f"  Interpretation: |r| << 1 => proxies are largely independent, "
      f"breaking the tautology.")

m["z_H_info_rti"] = stats.zscore(m["H_info_rti"])
m["z_H_info_eloundou"] = stats.zscore(m["H_info_eloundou"])

print("\n[5/6] Running v2.1 regressions...")

def ols(X, y):
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    sigma2 = (res ** 2).sum() / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = b / se
    p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))
    r2_v = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, se, t, p_two, r2_v

y = m["delta_emp_ann"].to_numpy()
ones = np.ones(len(m))

print("\n[Spec 1] delta_emp ~ alpha + beta * H_info_RTI  (RTI ALONE)")
X1 = np.column_stack([ones, m["H_info_rti"].to_numpy()])
b1, se1, t1, p_two1, r2_1 = ols(X1, y)
p_one1 = 1 - stats.t.cdf(t1[1], len(m) - 2)
print(f"  beta(H_info_RTI) = {b1[1]:+.4e}  SE {se1[1]:.4e}  "
      f"t = {t1[1]:+.3f}  p2 = {p_two1[1]:.4g}  p1(b>0) = {p_one1:.4g}")
print(f"  R^2 = {r2_1:.4f}")

print("\n[Spec 2] + GPT-gamma control (RTI is independent of AI-exposure)")
X2 = np.column_stack([ones, m["H_info_rti"].to_numpy(),
                      m["dv_rating_gamma"].to_numpy()])
b2, se2, t2, p_two2, r2_2 = ols(X2, y)
p_one2 = 1 - stats.t.cdf(t2[1], len(m) - 3)
print(f"  beta(H_info_RTI)   = {b2[1]:+.4e}  SE {se2[1]:.4e}  "
      f"t = {t2[1]:+.3f}  p1(b>0) = {p_one2:.4g}")
print(f"  gamma(GPT-gamma)   = {b2[2]:+.4e}  SE {se2[2]:.4e}  t = {t2[2]:+.3f}")
print(f"  R^2 = {r2_2:.4f}")

print("\n[Spec 3] Horse-race: RTI vs Eloundou H_info (both standardised)")
X3 = np.column_stack([ones, m["z_H_info_rti"].to_numpy(),
                      m["z_H_info_eloundou"].to_numpy()])
b3, se3, t3, p_two3, r2_3 = ols(X3, y)
print(f"  beta(z_H_info_RTI)       = {b3[1]:+.4e}  SE {se3[1]:.4e}  t = {t3[1]:+.3f}")
print(f"  beta(z_H_info_Eloundou)  = {b3[2]:+.4e}  SE {se3[2]:.4e}  t = {t3[2]:+.3f}")
print(f"  R^2 = {r2_3:.4f}")

# E_thermo_v2: enhanced multi-element including strength + bending + climbing
print("\n[6/6] Building E_thermo_v2 (enhanced with strength elements)...")
wc = pd.read_excel(os.path.join(onet, "Work Context.xlsx"))
THERMO_V2 = {
    "sitting":  ("4.C.2.d.1.a", "CX", -1),
    "standing": ("4.C.2.d.1.b", "CX", +1),
    "walking":  ("4.C.2.d.1.d", "CX", +1),
    "climbing": ("4.C.2.d.1.c", "CX", +1),
    "kneeling": ("4.C.2.d.1.e", "CX", +1),
    "bending":  ("4.C.2.d.1.h", "CX", +1),
    "repetitive": ("4.C.2.d.1.i", "CX", +1),
}
# also Work Activities strength elements
THERMO_V2_WA = {
    "physact":  ("4.A.3.a.1", "IM", +1),
    "handling": ("4.A.3.a.2", "IM", +1),
}

phys_components = []
for name, (eid, sc, sign) in THERMO_V2.items():
    sub = wc[(wc["Element ID"] == eid) & (wc["Scale ID"] == sc)].copy()
    sub["soc"] = sub["O*NET-SOC Code"].astype(str).str[:7]
    avg = sub.groupby("soc")["Data Value"].mean()
    phys_components.append((name, avg, sign))

for name, (eid, sc, sign) in THERMO_V2_WA.items():
    sub = wa[(wa["Element ID"] == eid) & (wa["Scale ID"] == sc)].copy()
    sub["soc"] = sub["O*NET-SOC Code"].astype(str).str[:7]
    avg = sub.groupby("soc")["Data Value"].mean()
    phys_components.append((name, avg, sign))

# Standardise + sum with signs
phys_df = pd.DataFrame({n: a for n, a, s in phys_components}).dropna()
phys_z = pd.DataFrame({n: stats.zscore(phys_df[n]) for n in phys_df.columns},
                       index=phys_df.index)
signs = {n: s for n, _, s in phys_components}
phys_z["E_thermo_v2"] = sum(signs[n] * phys_z[n] for n in phys_z.columns)
phys_z = phys_z.reset_index()

m2 = m.merge(phys_z[["soc", "E_thermo_v2"]], left_on="OCC_CODE",
             right_on="soc", how="inner").drop(columns=["soc"])
print(f"  E_thermo_v2 merged: N = {len(m2)}")

# E_thermo_v2 alone (does H4-thermo survive better measurement?)
X_t = np.column_stack([ones[:len(m2)], m2["E_thermo_v2"].to_numpy()])
y2 = m2["delta_emp_ann"].to_numpy()
b_t, se_t, t_t, p_two_t, r2_t = ols(X_t, y2)
p_one_t = 1 - stats.t.cdf(t_t[1], len(m2) - 2)
print(f"\n[Spec 4] delta_emp ~ alpha + beta * E_thermo_v2 (multi-element strength)")
print(f"  beta(E_thermo_v2) = {b_t[1]:+.4e}  SE {se_t[1]:.4e}  "
      f"t = {t_t[1]:+.3f}  p2 = {p_two_t[1]:.4g}  p1(b>0) = {p_one_t:.4g}")
print(f"  R^2 = {r2_t:.4f}")

# Save
out = {
    "v2.1": {
        "N_main": int(len(m)),
        "tautology_check": {
            "pearson_r_RTI_vs_Eloundou": float(r_proxy),
            "p": float(p_proxy),
            "interpretation":
                "Lower |r| means more independence, breaking the tautology.",
        },
        "spec_1_RTI_only": {
            "beta": float(b1[1]), "se": float(se1[1]), "t": float(t1[1]),
            "p_one_sided_positive": float(p_one1), "R2": float(r2_1),
        },
        "spec_2_RTI_plus_gamma_control": {
            "beta_RTI": float(b2[1]), "se_RTI": float(se2[1]),
            "t_RTI": float(t2[1]), "p_one_sided_positive": float(p_one2),
            "gamma_GPT": float(b2[2]), "R2": float(r2_2),
        },
        "spec_3_horse_race": {
            "beta_RTI": float(b3[1]), "p_RTI": float(p_two3[1]),
            "beta_Eloundou": float(b3[2]), "p_Eloundou": float(p_two3[2]),
            "R2": float(r2_3),
        },
        "spec_4_E_thermo_v2": {
            "N": int(len(m2)),
            "beta": float(b_t[1]), "se": float(se_t[1]), "t": float(t_t[1]),
            "p_one_sided_positive": float(p_one_t), "R2": float(r2_t),
        },
    },
}
out_path = os.path.join(base, "v21_rti_results.json")
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved -> {out_path}")

m_csv = m2[["OCC_CODE", "title_2024", "RTI", "H_info_rti",
            "H_info_eloundou", "dv_rating_gamma",
            "E_thermo_v2", "delta_emp_ann"]]
m_csv.to_csv(os.path.join(base, "v21_main_data.csv"), index=False)
print(f"Saved data -> v21_main_data.csv")
