"""
v1.2: Felten AIOE as alternative H_info proxy (multicollinearity-free
robustness check for the Eloundou-derived H_info).

v1.3: Industry-level fixed effects via inclusion of dominant-industry
NAICS dummies, drawn from BLS occupational employment by industry.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")

# ===== load IRI base =====
print("[v1.2] Loading IRI base + Felten AIOE...")
iri = pd.read_csv(os.path.join(base, "iri_score_table.csv"))
print(f"  IRI base: N = {len(iri)}")

aioe = pd.read_excel(os.path.join(base, "data/felten_aioe.xlsx"),
                     sheet_name="Appendix A")
aioe = aioe.rename(columns={"SOC Code": "OCC_CODE"})
aioe["OCC_CODE"] = aioe["OCC_CODE"].astype(str).str.strip()
aioe = aioe[["OCC_CODE", "AIOE"]].drop_duplicates(subset=["OCC_CODE"])
print(f"  AIOE cleaned: {len(aioe)} SOC codes, "
      f"range [{aioe['AIOE'].min():.3f}, {aioe['AIOE'].max():.3f}]")

# Merge with IRI
m = iri.merge(aioe, on="OCC_CODE", how="inner")
print(f"  Merged IRI x AIOE: N = {len(m)}")

# H_info_alt = -AIOE (lower AI exposure -> higher informational entropy)
# Eloundou H_info and -AIOE should correlate but not be identical
m["H_info_alt"] = -m["AIOE"]  # higher = less AI-exposed
m["z_H_info_alt"] = stats.zscore(m["H_info_alt"])

# Correlation between Eloundou-based and Felten-based proxies
r_proxy, p_proxy = stats.pearsonr(m["z_H_info"].to_numpy(),
                                   m["z_H_info_alt"].to_numpy())
print(f"\n  z(H_info[Eloundou]) vs z(H_info[Felten]): r = {r_proxy:+.4f}, p = {p_proxy:.4g}")

# IRI_alt = z(H_info_alt) + z(JobZone) + z(log wage)
m["IRI_alt"] = m["z_H_info_alt"] + m["z_job_zone"] + m["z_log_wage"]
r_alt, p_alt = stats.pearsonr(m["IRI_alt"].to_numpy(),
                               m["delta_emp_ann"].to_numpy())
r_alt_s, p_alt_s = stats.spearmanr(m["IRI_alt"].to_numpy(),
                                    m["delta_emp_ann"].to_numpy())
r_orig = stats.pearsonr(m["IRI"].to_numpy(),
                         m["delta_emp_ann"].to_numpy())[0]

print(f"\n  IRI_alt (Felten-based) vs delta_emp: r = {r_alt:+.4f}, p = {p_alt:.4g}")
print(f"                                        rho = {r_alt_s:+.4f}, p = {p_alt_s:.4g}")
print(f"  IRI (Eloundou-based, original) vs delta_emp: r = {r_orig:+.4f}")

# Joint regression: both H_info proxies + JobZone + log_wage
X = np.column_stack([np.ones(len(m)), m["z_H_info"].to_numpy(),
                     m["z_H_info_alt"].to_numpy(),
                     m["z_job_zone"].to_numpy(), m["z_log_wage"].to_numpy()])
y = m["delta_emp_ann"].to_numpy()
b, *_ = np.linalg.lstsq(X, y, rcond=None)
res = y - X @ b
n, k = X.shape
sigma2 = (res ** 2).sum() / (n - k)
cov = sigma2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
t = b / se
p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))
r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
print(f"\n  Joint OLS (both proxies):")
labels = ["intercept", "z_H_info(Eloundou)", "z_H_info(Felten)", "z_JobZone", "z_log_wage"]
for j in range(k):
    print(f"    {labels[j]:25s}: b = {b[j]:+.4e}  SE {se[j]:.4e}  "
          f"t = {t[j]:+.3f}  p2 = {p_two[j]:.4g}")
print(f"  R^2 = {r2:.4f}")

# ===== v1.3: Industry FE =====
# Need dominant industry per occupation. BLS national-detailed cross-industry
# only gives one row per occ. Use industry-level rows from same xlsx.
print("\n\n[v1.3] Loading BLS 2024 for industry-level data...")
df24 = pd.read_excel(os.path.join(base, "data/bls_2024/oesm24all/all_data_M_2024.xlsx"))
df24.columns = df24.columns.str.upper()

# Industry-specific national rows (NAICS != "000000" and AREA_TYPE == 1)
ind = df24[(df24["AREA_TYPE"] == 1)
           & (df24["O_GROUP"].astype(str).str.lower() == "detailed")
           & (df24["I_GROUP"].astype(str).str.lower() == "4-digit")].copy()
ind["TOT_EMP"] = pd.to_numeric(ind["TOT_EMP"], errors="coerce")
ind = ind.dropna(subset=["TOT_EMP", "OCC_CODE", "NAICS"])
ind = ind[ind["TOT_EMP"] > 0]
print(f"  Industry-level rows: {len(ind):,}")

# Largest-industry NAICS per occupation
top_ind = (ind.sort_values("TOT_EMP", ascending=False)
              .groupby("OCC_CODE")
              .first()
              .reset_index()[["OCC_CODE", "NAICS", "NAICS_TITLE"]])
top_ind["NAICS_2"] = top_ind["NAICS"].astype(str).str[:2]
print(f"  occupations with dominant NAICS: {len(top_ind)}")

m2 = m.merge(top_ind[["OCC_CODE", "NAICS_2", "NAICS_TITLE"]], on="OCC_CODE", how="inner")
print(f"  IRI x AIOE x dominant-NAICS: N = {len(m2)}")
print(f"  NAICS_2 distribution top 8:")
print(m2["NAICS_2"].value_counts().head(8).to_string())

# OLS with industry FE: delta_emp ~ IRI + I(NAICS_2)
# Use one-hot for NAICS_2
naics_dummies = pd.get_dummies(m2["NAICS_2"], prefix="naics2", drop_first=True).astype(float)
X_fe = np.column_stack([np.ones(len(m2)), m2["IRI"].to_numpy(),
                        naics_dummies.to_numpy()])
y_fe = m2["delta_emp_ann"].to_numpy()
b_fe, *_ = np.linalg.lstsq(X_fe, y_fe, rcond=None)
res_fe = y_fe - X_fe @ b_fe
n_fe, k_fe = X_fe.shape
sigma2_fe = (res_fe ** 2).sum() / (n_fe - k_fe)
cov_fe = sigma2_fe * np.linalg.inv(X_fe.T @ X_fe)
se_fe = np.sqrt(np.diag(cov_fe))
t_fe = b_fe / se_fe
p_two_fe = 2 * (1 - stats.t.cdf(np.abs(t_fe), n_fe - k_fe))
r2_fe = 1 - (res_fe ** 2).sum() / ((y_fe - y_fe.mean()) ** 2).sum()

print(f"\n  Industry-FE OLS (delta_emp ~ IRI + 2-digit NAICS dummies, N={n_fe})")
print(f"    beta(IRI) = {b_fe[1]:+.4e}  SE {se_fe[1]:.4e}  t = {t_fe[1]:+.3f}  p2 = {p_two_fe[1]:.4g}")
print(f"    R^2 (overall) = {r2_fe:.4f}")
# How much R^2 is added by IRI vs FE alone
X_fe_only = np.column_stack([np.ones(len(m2)), naics_dummies.to_numpy()])
b_only, *_ = np.linalg.lstsq(X_fe_only, y_fe, rcond=None)
res_only = y_fe - X_fe_only @ b_only
r2_fe_only = 1 - (res_only ** 2).sum() / ((y_fe - y_fe.mean()) ** 2).sum()
print(f"    R^2 (FE alone, no IRI) = {r2_fe_only:.4f}")
print(f"    R^2 increment from IRI = {r2_fe - r2_fe_only:.4f}")

# Save
out = {
    "v1.2_alt_proxy": {
        "N": int(len(m)),
        "proxy_correlation_eloundou_vs_felten": {"r": float(r_proxy), "p": float(p_proxy)},
        "IRI_eloundou_r": float(r_orig),
        "IRI_felten_r": float(r_alt),
        "IRI_felten_rho": float(r_alt_s),
        "joint_OLS": {
            "labels": labels,
            "b": [float(x) for x in b],
            "se": [float(x) for x in se],
            "t": [float(x) for x in t],
            "p_two": [float(x) for x in p_two],
            "R2": float(r2),
        },
    },
    "v1.3_industry_FE": {
        "N": int(n_fe),
        "beta_IRI": float(b_fe[1]),
        "se_IRI": float(se_fe[1]),
        "t_IRI": float(t_fe[1]),
        "p_two_IRI": float(p_two_fe[1]),
        "R2_with_FE": float(r2_fe),
        "R2_FE_only": float(r2_fe_only),
        "R2_increment_from_IRI": float(r2_fe - r2_fe_only),
        "n_naics_dummies": int(naics_dummies.shape[1]),
    },
}
out_path = os.path.join(base, "v12_v13_results.json")
with open(out_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\nResults saved -> {out_path}")
