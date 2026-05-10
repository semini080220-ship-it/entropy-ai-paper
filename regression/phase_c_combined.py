"""
Phase C combined-entropy regression.

Two definitions of occupational entropy:
  E^thermo : metabolic dissipation (J/h)  -- already in phase_b_final.csv
  H^info   : task informational entropy (proxy = 1 - Eloundou alpha,
             bounded 0-1; high = task is non-routine, hard for LLM)
  E^combined = z(E^thermo) + z(H^info)

Regression specs:
  1. Delta_emp ~ E^thermo                        (replicates Phase B baseline)
  2. Delta_emp ~ H^info                          (info-only)
  3. Delta_emp ~ E^combined                      (combined index)
  4. Delta_emp ~ E^thermo + H^info               (both, additive)
  5. spec 4 + GPT-gamma control                  (AI-attributable component)
  6. spec 4 + GPT-beta  control                  (medium AI control)

H4 (combined form): occupations with higher combined entropy are
  differentially preserved -> beta on E^combined > 0; both component
  beta's positive in spec 4.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")

# Load Phase B merged frame (BLS x O*NET physical)
final = pd.read_csv(os.path.join(base, "phase_b_final.csv"))
final = final.rename(columns={"E_human": "E_thermo"})

# Load Eloundou GPT exposure
elo = pd.read_csv(os.path.join(base, "data/eloundou_occ_level.csv"))
elo["soc"] = elo["O*NET-SOC Code"].astype(str).str[:7]
elo_agg = elo.groupby("soc")[["dv_rating_alpha", "dv_rating_beta",
                              "dv_rating_gamma"]].mean().reset_index()

m = final.merge(elo_agg, left_on="OCC_CODE", right_on="soc", how="inner")

# H_info = 1 - alpha (informational entropy proxy)
m["H_info"] = 1.0 - m["dv_rating_alpha"]

# Standardised z-scores
def z(x):
    return (x - x.mean()) / x.std(ddof=0)

m["z_E_thermo"] = z(m["E_thermo"])
m["z_H_info"] = z(m["H_info"])
m["E_combined"] = m["z_E_thermo"] + m["z_H_info"]

print(f"Sample N = {len(m)}")
print("\nSummary statistics:")
print(m[["E_thermo", "H_info", "E_combined", "delta_emp_ann"]].describe())
print("\nCorrelations:")
print(m[["E_thermo", "H_info", "E_combined", "delta_emp_ann",
         "dv_rating_alpha", "dv_rating_beta", "dv_rating_gamma"]].corr().round(3))


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


y = m["delta_emp_ann"].to_numpy()
ones = np.ones(len(m))

specs = {
    "1: E_thermo only":
        np.column_stack([ones, m["E_thermo"].to_numpy()]),
    "2: H_info only":
        np.column_stack([ones, m["H_info"].to_numpy()]),
    "3: E_combined":
        np.column_stack([ones, m["E_combined"].to_numpy()]),
    "4: E_thermo + H_info":
        np.column_stack([ones, m["E_thermo"].to_numpy(), m["H_info"].to_numpy()]),
    "5: 4 + gamma control":
        np.column_stack([ones, m["E_thermo"].to_numpy(), m["H_info"].to_numpy(),
                         m["dv_rating_gamma"].to_numpy()]),
    "6: 4 + beta control":
        np.column_stack([ones, m["E_thermo"].to_numpy(), m["H_info"].to_numpy(),
                         m["dv_rating_beta"].to_numpy()]),
}

results = {"N": int(len(m)), "specs": {}}

print("\n" + "=" * 64)
print("Phase C combined-entropy regressions (N = {})".format(len(m)))
print("=" * 64)
for label, X in specs.items():
    b, se, t, p_two, r2 = ols(X, y)
    n, k = X.shape
    p_one = [1 - stats.t.cdf(t[j], n - k) for j in range(k)]
    print(f"\n[{label}]")
    print(f"  R^2 = {r2:.4f}")
    coef_names = (
        ["intercept"] + (
            ["E_thermo"] if k == 2 and label.startswith("1") else
            ["H_info"] if k == 2 and label.startswith("2") else
            ["E_combined"] if k == 2 and label.startswith("3") else
            ["E_thermo", "H_info"] if k == 3 else
            ["E_thermo", "H_info", "GPT_gamma"] if "5" in label else
            ["E_thermo", "H_info", "GPT_beta"]
        )
    )
    for j in range(k):
        print(f"  {coef_names[j]:14s}: b = {b[j]:+.4e}  SE {se[j]:.4e}  "
              f"t = {t[j]:+.3f}  p2 = {p_two[j]:.4g}  p1(b>0) = {p_one[j]:.4g}")
    results["specs"][label] = {
        "R_squared": float(r2),
        "coefs": {coef_names[j]: {
            "b": float(b[j]),
            "se": float(se[j]),
            "t": float(t[j]),
            "p_two": float(p_two[j]),
            "p_one_positive": float(p_one[j]),
        } for j in range(k)},
    }

# Verdict on combined index
b_combined = results["specs"]["3: E_combined"]["coefs"]["E_combined"]
if b_combined["b"] > 0 and b_combined["p_one_positive"] < 0.05:
    v = (f"H4 (combined) CONFIRMED: beta on E_combined = {b_combined['b']:+.4e}, "
         f"one-sided p = {b_combined['p_one_positive']:.4g}")
elif b_combined["b"] > 0 and b_combined["p_one_positive"] < 0.10:
    v = f"H4 (combined) MARGINAL: p_one = {b_combined['p_one_positive']:.4g}"
elif b_combined["b"] > 0:
    v = f"H4 (combined) sign positive but ns: p_one = {b_combined['p_one_positive']:.4g}"
else:
    v = "H4 (combined) sign negative on combined index"
print(f"\nCombined-index verdict: {v}")
results["combined_verdict"] = v

out = os.path.join(base, "phase_c_combined_results.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults JSON -> {out}")
