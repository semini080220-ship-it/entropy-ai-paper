"""
Phase A pilot regression on 10 occupations from paper.md §7.4.
Tests H4: Delta_employment = alpha + beta * E^human, predicting beta > 0.
N=10 — sign-verification only; full BLS regression is Phase B.
"""
import json
import os
import numpy as np
from scipy import stats

# Data from paper §7.4 (BLS 2019-2025 annualised; E^human from O*NET-MET)
data = [
    ("43-2011", "Call-center agent",        5.0e5, -0.07),
    ("43-9061", "Office clerk, general",    5.0e5, -0.04),
    ("27-3091", "Interpreter / translator", 5.0e5, -0.08),
    ("15-1252", "Software dev. (junior)",   5.0e5,  0.00),
    ("35-1011", "Chef / pastry chef",       9.0e5,  0.01),
    ("47-2152", "Plumber",                  1.2e6,  0.02),
    ("47-2111", "Electrician",              1.0e6,  0.015),
    ("29-1141", "Registered nurse",         8.0e5,  0.06),
    ("31-1121", "Home health aide",         9.0e5,  0.12),
    ("53-3032", "Heavy truck driver",       6.0e5, -0.01),
]

e_human = np.array([r[2] for r in data])
d_emp   = np.array([r[3] for r in data])
n = len(data)

# OLS via normal equations
X = np.column_stack([np.ones(n), e_human])
beta, *_ = np.linalg.lstsq(X, d_emp, rcond=None)
alpha, slope = beta
res = d_emp - X @ beta
sigma2 = (res ** 2).sum() / (n - 2)
cov = sigma2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
t_stat = beta / se
p_two = 2 * (1 - stats.t.cdf(np.abs(t_stat), n - 2))
p_one_sided_positive = 1 - stats.t.cdf(t_stat[1], n - 2)  # H4: beta > 0

ss_total = ((d_emp - d_emp.mean()) ** 2).sum()
r2 = 1 - (res ** 2).sum() / ss_total

r_p, p_p = stats.pearsonr(e_human, d_emp)
r_s, p_s = stats.spearmanr(e_human, d_emp)

print("=" * 64)
print(f"Phase A -- Pilot Regression (N={n} occupations from sec.7.4)")
print("=" * 64)
print()
print("Model: Delta_employment = alpha + beta * E^human")
print()
print(f"  alpha (intercept)     : {alpha:+.6f}   (SE {se[0]:.6f})")
print(f"  beta  (slope, E^human): {slope:+.4e}   (SE {se[1]:.4e})")
print(f"  t-statistic on beta   : {t_stat[1]:+.3f}")
print(f"  p-value (two-sided)   : {p_two[1]:.4f}")
print(f"  p-value (one-sided H4): {p_one_sided_positive:.4f}")
print(f"  R^2                   : {r2:.3f}")
print()
print(f"Pearson  r(E^human, Delta_emp) = {r_p:+.3f}, p = {p_p:.4f}")
print(f"Spearman rho                   = {r_s:+.3f}, p = {p_s:.4f}")
print()

# Verdict
if slope > 0:
    if p_one_sided_positive < 0.05:
        v = f"H4 CONFIRMED at one-sided alpha=0.05 (beta>0, p={p_one_sided_positive:.4f})"
    elif p_one_sided_positive < 0.10:
        v = f"H4 MARGINAL — beta>0 but p={p_one_sided_positive:.4f} (one-sided)"
    else:
        v = f"H4 sign correct but underpowered (N={n}); p={p_one_sided_positive:.4f}"
else:
    v = f"H4 REJECTED at this sample (beta<0, opposite of prediction)"
print("Verdict:", v)

# Save JSON for paper integration
results = {
    "phase": "A_pilot",
    "N": n,
    "alpha": float(alpha),
    "se_alpha": float(se[0]),
    "beta": float(slope),
    "se_beta": float(se[1]),
    "t_beta": float(t_stat[1]),
    "p_two_sided": float(p_two[1]),
    "p_one_sided_positive": float(p_one_sided_positive),
    "R_squared": float(r2),
    "pearson_r": float(r_p),
    "pearson_p": float(p_p),
    "spearman_rho": float(r_s),
    "spearman_p": float(p_s),
    "verdict": v,
    "data": [
        {"soc": d[0], "title": d[1], "E_human_J_per_h": d[2], "delta_emp": d[3]}
        for d in data
    ],
}
out = os.path.expanduser("~/Desktop/entropy-ai-paper/regression/phase_a_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved -> {out}")
