"""
v2.2 — Reconstruct IRI using the AI-free RTI-based H_info as primary
input, replacing the v1.1 Eloundou-based H_info.

  IRI_v2_i = z(H_info_RTI_i) + z(JobZone_i) + z(log w_i)

This makes the IRI itself fully AI-content-free at construction time,
addressing the v2.0 tautology critique at the index level.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
onet = os.path.join(base, "data/onet/db_30_2_excel")
bls_24 = os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx")

print("[1/5] Loading components...")
v21 = pd.read_csv(os.path.join(base, "v21_main_data.csv"))
print(f"  v21 main data: N = {len(v21)}, cols = {v21.columns.tolist()}")

# Job Zones
jz = pd.read_excel(os.path.join(onet, "Job Zones.xlsx"))
jz["soc"] = jz["O*NET-SOC Code"].astype(str).str[:7]
jz_agg = jz.groupby("soc")["Job Zone"].mean().reset_index()
jz_agg.columns = ["soc_jz", "job_zone"]

print("[2/5] Loading BLS 2024 wages (~30s)...")
df24 = pd.read_excel(bls_24)
df24.columns = df24.columns.str.upper()
n24 = df24[(df24["AREA_TYPE"] == 1)
           & (df24["O_GROUP"].astype(str).str.lower() == "detailed")
           & (df24["I_GROUP"].astype(str).str.lower() == "cross-industry")].copy()
n24["A_MEDIAN"] = pd.to_numeric(n24["A_MEDIAN"], errors="coerce")
n24 = n24.dropna(subset=["OCC_CODE", "A_MEDIAN"])
n24 = n24[n24["A_MEDIAN"] > 0]
wage = n24[["OCC_CODE", "A_MEDIAN"]].rename(columns={"A_MEDIAN": "wage_median"})

print("[3/5] Building IRI v2 with RTI-based H_info as primary...")
m = v21.merge(jz_agg, left_on="OCC_CODE", right_on="soc_jz", how="inner")
m = m.merge(wage, on="OCC_CODE", how="inner")
m = m.dropna(subset=["H_info_rti", "job_zone", "wage_median"])
print(f"  N = {len(m)}")

m["log_wage"] = np.log(m["wage_median"])
m["z_H_info_rti"] = stats.zscore(m["H_info_rti"])
m["z_H_info_eloundou"] = stats.zscore(m["H_info_eloundou"])
m["z_job_zone"] = stats.zscore(m["job_zone"])
m["z_log_wage"] = stats.zscore(m["log_wage"])

m["IRI_v2"] = m["z_H_info_rti"] + m["z_job_zone"] + m["z_log_wage"]
m["IRI_v1"] = m["z_H_info_eloundou"] + m["z_job_zone"] + m["z_log_wage"]
m["IRI_v2_pct"] = m["IRI_v2"].rank(pct=True) * 100

print("\n[4/5] Validation...")
y = m["delta_emp_ann"].to_numpy()

# IRI v2 (RTI-based, AI-free)
r_v2, p_v2 = stats.pearsonr(m["IRI_v2"].to_numpy(), y)
rho_v2, p_rho2 = stats.spearmanr(m["IRI_v2"].to_numpy(), y)

# IRI v1 (Eloundou-based, original) for comparison
r_v1, p_v1 = stats.pearsonr(m["IRI_v1"].to_numpy(), y)

# Cross-correlation between v1 and v2
r_iri, _ = stats.pearsonr(m["IRI_v1"].to_numpy(), m["IRI_v2"].to_numpy())

print(f"  IRI_v2 (RTI-based, AI-FREE) vs delta_emp:")
print(f"    Pearson  r = {r_v2:+.4f}, p = {p_v2:.4g}")
print(f"    Spearman rho = {rho_v2:+.4f}, p = {p_rho2:.4g}")
print(f"  IRI_v1 (Eloundou-based, original):")
print(f"    Pearson  r = {r_v1:+.4f}, p = {p_v1:.4g}")
print(f"  Cross-correlation IRI_v1 vs IRI_v2: r = {r_iri:+.4f}")

print("\n  Top 10 IRI_v2:")
top = m.nlargest(10, "IRI_v2")[["OCC_CODE", "title_2024", "H_info_rti",
                                  "job_zone", "wage_median", "IRI_v2",
                                  "IRI_v2_pct", "delta_emp_ann"]]
print(top.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n  Bottom 10 IRI_v2:")
bot = m.nsmallest(10, "IRI_v2")[["OCC_CODE", "title_2024", "H_info_rti",
                                  "job_zone", "wage_median", "IRI_v2",
                                  "IRI_v2_pct", "delta_emp_ann"]]
print(bot.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

print("\n[5/5] Saving...")
out_csv = os.path.join(base, "iri_v2_score_table.csv")
out_df = m[["OCC_CODE", "title_2024", "H_info_rti", "H_info_eloundou",
            "job_zone", "wage_median", "z_H_info_rti", "z_job_zone",
            "z_log_wage", "IRI_v2", "IRI_v2_pct", "IRI_v1",
            "delta_emp_ann"]].sort_values("IRI_v2", ascending=False)
out_df.to_csv(out_csv, index=False)
print(f"  Saved: {out_csv}")

results = {
    "v2.2_IRI_v2": {
        "N": len(m),
        "formula": "IRI_v2 = z(H_info_RTI) + z(JobZone) + z(log wage)",
        "primary_proxy": "H_info_RTI = -RTI (AI-content-free, from O*NET only)",
        "validation": {
            "pearson_r": float(r_v2), "p_pearson": float(p_v2),
            "spearman_rho": float(rho_v2), "p_spearman": float(p_rho2),
        },
        "comparison_to_v1": {
            "IRI_v1_r": float(r_v1), "IRI_v1_p": float(p_v1),
            "cross_correlation": float(r_iri),
        },
        "top10": top[["OCC_CODE", "title_2024", "IRI_v2",
                       "IRI_v2_pct"]].to_dict(orient="records"),
        "bottom10": bot[["OCC_CODE", "title_2024", "IRI_v2",
                          "IRI_v2_pct"]].to_dict(orient="records"),
    },
}
with open(os.path.join(base, "iri_v2_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"  Saved: iri_v2_results.json")
