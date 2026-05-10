"""
Phase D: Informational Resilience Index (IRI) construction and validation.

  IRI_i = z(H_info_i) + z(JobZone_i) + z(log wage_i)
       = z(1 - alpha_i) + z(O*NET Job Zone) + z(log BLS A_MEDIAN)

Unit weights (theoretical neutrality). Robustness: regression-fitted
weights and PCA first component.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
onet = os.path.join(base, "data/onet/db_30_2_excel")
bls_24 = os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx")

# Phase B merged (BLS x O*NET physical) as base
print("[1/6] Loading Phase B base...")
final = pd.read_csv(os.path.join(base, "phase_b_final.csv"))
final = final.rename(columns={"E_human": "E_thermo"})
print(f"  Phase B base: N = {len(final)}")

# Eloundou
print("\n[2/6] Loading Eloundou exposure...")
elo = pd.read_csv(os.path.join(base, "data/eloundou_occ_level.csv"))
elo["soc"] = elo["O*NET-SOC Code"].astype(str).str[:7]
elo_agg = elo.groupby("soc")[["dv_rating_alpha"]].mean().reset_index()
elo_agg["H_info"] = 1.0 - elo_agg["dv_rating_alpha"]
print(f"  Eloundou aggregated: {len(elo_agg)} SOCs")

# Job Zones
print("\n[3/6] Loading O*NET Job Zones...")
jz = pd.read_excel(os.path.join(onet, "Job Zones.xlsx"))
print(f"  columns: {jz.columns.tolist()}")
jz["soc"] = jz["O*NET-SOC Code"].astype(str).str[:7]
jz_agg = jz.groupby("soc")["Job Zone"].mean().reset_index()
jz_agg.columns = ["soc_jz", "job_zone"]
print(f"  Job Zones: {len(jz_agg)} SOCs, "
      f"range [{jz_agg['job_zone'].min()}, {jz_agg['job_zone'].max()}]")

# BLS wages (need to load 2024 again, ~30s)
print("\n[4/6] Loading BLS 2024 wages (~30s)...")
df24 = pd.read_excel(bls_24)
df24.columns = df24.columns.str.upper()
n24 = df24[(df24["AREA_TYPE"] == 1)
           & (df24["O_GROUP"].astype(str).str.lower() == "detailed")
           & (df24["I_GROUP"].astype(str).str.lower() == "cross-industry")].copy()
n24["A_MEDIAN"] = pd.to_numeric(n24["A_MEDIAN"], errors="coerce")
n24 = n24.dropna(subset=["OCC_CODE", "A_MEDIAN"])
n24 = n24[n24["A_MEDIAN"] > 0]
wage = n24[["OCC_CODE", "A_MEDIAN"]].rename(columns={"A_MEDIAN": "wage_median"})
print(f"  Wages: {len(wage)} SOCs, "
      f"range [${wage['wage_median'].min():,.0f}, ${wage['wage_median'].max():,.0f}]")

# Merge all
print("\n[5/6] Merging components...")
m = final.merge(elo_agg[["soc", "H_info"]], left_on="OCC_CODE", right_on="soc")
m = m.merge(jz_agg, left_on="OCC_CODE", right_on="soc_jz", how="inner")
m = m.merge(wage, on="OCC_CODE", how="inner")
m = m.dropna(subset=["H_info", "job_zone", "wage_median"])
print(f"  Final IRI sample: N = {len(m)}")

# Build IRI
print("\n[6/6] Constructing IRI...")
m["log_wage"] = np.log(m["wage_median"])
m["z_H_info"] = stats.zscore(m["H_info"])
m["z_job_zone"] = stats.zscore(m["job_zone"])
m["z_log_wage"] = stats.zscore(m["log_wage"])

# Unit-weight IRI
m["IRI"] = m["z_H_info"] + m["z_job_zone"] + m["z_log_wage"]
m["IRI_percentile"] = m["IRI"].rank(pct=True) * 100

# Validation
r_p, p_p = stats.pearsonr(m["IRI"].to_numpy(), m["delta_emp_ann"].to_numpy())
r_s, p_s = stats.spearmanr(m["IRI"].to_numpy(), m["delta_emp_ann"].to_numpy())

# Robustness: regression-fitted weights
X = np.column_stack([np.ones(len(m)), m["z_H_info"].to_numpy(),
                     m["z_job_zone"].to_numpy(), m["z_log_wage"].to_numpy()])
y = m["delta_emp_ann"].to_numpy()
b, *_ = np.linalg.lstsq(X, y, rcond=None)
m["IRI_reg"] = b[1]*m["z_H_info"] + b[2]*m["z_job_zone"] + b[3]*m["z_log_wage"]
r_reg, _ = stats.pearsonr(m["IRI_reg"].to_numpy(), y)

# Robustness: PCA first component
Z = m[["z_H_info", "z_job_zone", "z_log_wage"]].to_numpy()
cov = np.cov(Z.T)
evals, evecs = np.linalg.eig(cov)
order = np.argsort(evals.real)[::-1]
pc1_w = evecs[:, order[0]].real
# orient so that PC1 weights sum positive (interpretation)
if pc1_w.sum() < 0:
    pc1_w = -pc1_w
m["IRI_pca"] = Z @ pc1_w
r_pca, _ = stats.pearsonr(m["IRI_pca"].to_numpy(), y)

# Print results
print()
print("=" * 70)
print(f"IRI = z(H_info) + z(JobZone) + z(log wage), unit weights")
print("=" * 70)
print(f"\nN = {len(m)}")
print(f"\nIRI vs Delta_emp (validation):")
print(f"  Pearson r  = {r_p:+.4f}  (p = {p_p:.4g})")
print(f"  Spearman rho = {r_s:+.4f}  (p = {p_s:.4g})")

print(f"\nRobustness:")
print(f"  Reg-fitted weights: H_info={b[1]:+.4f}, JobZone={b[2]:+.4f}, log_wage={b[3]:+.4f}")
print(f"    pearson r = {r_reg:+.4f}")
print(f"  PCA first component weights (oriented): {pc1_w.round(4)}")
print(f"    pearson r = {r_pca:+.4f}")

print("\nTop 10 IRI (most resilient to AI):")
top = m.nlargest(10, "IRI")[["OCC_CODE", "title_2024", "H_info", "job_zone",
                              "wage_median", "IRI", "IRI_percentile",
                              "delta_emp_ann"]]
print(top.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

print("\nBottom 10 IRI (most exposed to AI):")
bot = m.nsmallest(10, "IRI")[["OCC_CODE", "title_2024", "H_info", "job_zone",
                               "wage_median", "IRI", "IRI_percentile",
                               "delta_emp_ann"]]
print(bot.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# Save
out_csv = os.path.join(base, "iri_score_table.csv")
out = m[["OCC_CODE", "title_2024", "H_info", "job_zone", "wage_median",
         "z_H_info", "z_job_zone", "z_log_wage",
         "IRI", "IRI_percentile", "IRI_reg", "IRI_pca",
         "delta_emp_ann"]].sort_values("IRI", ascending=False)
out.to_csv(out_csv, index=False)
print(f"\nIRI table -> {out_csv}")

results = {
    "N": int(len(m)),
    "formula": "IRI = z(H_info) + z(JobZone) + z(log wage), unit weight",
    "components": ["H_info = 1 - Eloundou alpha",
                   "JobZone (O*NET 1-5)",
                   "log(BLS A_MEDIAN annual wage)"],
    "validation": {
        "pearson_r": float(r_p), "p_pearson": float(p_p),
        "spearman_rho": float(r_s), "p_spearman": float(p_s),
    },
    "robustness": {
        "regression_fitted": {
            "weights": {"H_info": float(b[1]), "JobZone": float(b[2]),
                        "log_wage": float(b[3])},
            "pearson_r": float(r_reg),
        },
        "PCA_first_component": {
            "weights_oriented": [float(x) for x in pc1_w],
            "pearson_r": float(r_pca),
        },
    },
    "summary": {
        "IRI_mean": float(m["IRI"].mean()),
        "IRI_std": float(m["IRI"].std()),
        "IRI_min": float(m["IRI"].min()),
        "IRI_max": float(m["IRI"].max()),
    },
    "top10": top[["OCC_CODE", "title_2024", "IRI", "IRI_percentile"]].to_dict(orient="records"),
    "bottom10": bot[["OCC_CODE", "title_2024", "IRI", "IRI_percentile"]].to_dict(orient="records"),
}
with open(os.path.join(base, "iri_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"IRI results JSON -> iri_results.json")
