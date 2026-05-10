"""
Phase B with control: regress delta_emp on E^human controlling for Eloundou
GPT exposure, isolating the AI-attributable variation in employment change.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")

# Load Phase B merged data
final = pd.read_csv(os.path.join(base, "phase_b_final.csv"))
print(f"Phase B final loaded: N = {len(final)}")

# Load Eloundou GPT exposure
elo = pd.read_csv(os.path.join(base, "data/eloundou_occ_level.csv"))
elo["soc"] = elo["O*NET-SOC Code"].astype(str).str[:7]
exp_cols = ["dv_rating_alpha", "dv_rating_beta", "dv_rating_gamma"]
elo_agg = elo.groupby("soc")[exp_cols].mean().reset_index()
print(f"Eloundou: {len(elo_agg)} SOCs")

m = final.merge(elo_agg, left_on="OCC_CODE", right_on="soc", how="inner")
print(f"Merged: N = {len(m)}\n")


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

# Spec 1: baseline (replicate Phase B)
X1 = np.column_stack([np.ones(len(m)), m["E_human"].to_numpy()])
b1, se1, t1, p1, r1 = ols(X1, y)
print("=" * 64)
print("[Spec 1] delta_emp = alpha + beta * E^human")
print("=" * 64)
print(f"  beta(E^human) = {b1[1]:+.4e}  SE {se1[1]:.4e}")
print(f"  t = {t1[1]:+.3f}   p_two = {p1[1]:.4g}")
print(f"  R^2 = {r1:.4f}")

# Spec 2: controlled
results = {
    "N": int(len(m)),
    "spec_1_uncontrolled": {
        "beta_E_human": float(b1[1]),
        "se": float(se1[1]),
        "t": float(t1[1]),
        "p_two_sided": float(p1[1]),
        "R_squared": float(r1),
    },
}

for ctrl in exp_cols:
    X2 = np.column_stack([np.ones(len(m)), m["E_human"].to_numpy(), m[ctrl].to_numpy()])
    b2, se2, t2, p2, r2v = ols(X2, y)
    p_one_b = 1 - stats.t.cdf(t2[1], len(m) - 3)
    print()
    print("=" * 64)
    print(f"[Spec 2:{ctrl}]  delta_emp = alpha + beta * E^human + gamma * GPT_exposure")
    print("=" * 64)
    print(f"  beta (E^human)         = {b2[1]:+.4e}  SE {se2[1]:.4e}  t={t2[1]:+.3f}  p2={p2[1]:.4g}  p_one(b>0)={p_one_b:.4g}")
    print(f"  gamma ({ctrl}) = {b2[2]:+.4e}  SE {se2[2]:.4e}  t={t2[2]:+.3f}  p2={p2[2]:.4g}")
    print(f"  R^2 = {r2v:.4f}")
    results[f"spec_2_{ctrl}"] = {
        "beta_E_human": float(b2[1]),
        "se_beta_E_human": float(se2[1]),
        "t_beta_E_human": float(t2[1]),
        "p_two_sided_beta": float(p2[1]),
        "p_one_sided_positive_beta": float(p_one_b),
        "gamma_GPT_exposure": float(b2[2]),
        "p_gamma": float(p2[2]),
        "R_squared": float(r2v),
    }

# Verdict
beta_signs = []
for k, v in results.items():
    if k.startswith("spec_") and "beta_E_human" in v:
        beta_signs.append(v["beta_E_human"])

if all(b > 0 for b in beta_signs):
    verdict = "H4 sign positive across all specifications -- direction supported"
elif all(b < 0 for b in beta_signs):
    verdict = "H4 sign negative across all specifications -- consistently falsified"
else:
    verdict = "H4 sign flips across specifications -- ambiguous; control matters"
print(f"\nVerdict: {verdict}")
results["verdict"] = verdict

out = os.path.join(base, "phase_b_with_control_results.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults JSON -> {out}")
