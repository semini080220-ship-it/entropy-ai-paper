"""
v2.8 - Pre-trends placebo: does the H4-info effect appear in the
       PRE-ChatGPT period (2014-2019) too?

  Run the same v2.7 ISCO 2-digit cross-country regression on:
    Pre-period:  2014 -> 2019 (5-year window, ChatGPT released Nov 2022)
    Post-period: 2019 -> 2024 (5-year window, includes ChatGPT)

  Three possible outcomes:
    (a) beta_pre approx 0, beta_post >> 0
        => H4-info is genuinely AI-driven (post-2022 effect).
    (b) beta_pre approx beta_post > 0
        => H4-info is a deep long-run routinizability gradient
           (automation/offshoring/ageing); AI is incidental.
    (c) beta_pre > beta_post > 0
        => H4-info effect is decelerating (unlikely).

  This is the cleanest causal test we can do with public data, and it
  determines the paper's narrative.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
tsv = os.path.join(base, "data/eurostat_lfsa_egai2d.tsv")

print("[1/5] Parsing Eurostat panel for multiple periods...")
df = pd.read_csv(tsv, sep="\t", na_values=[":"], dtype=str)
key_col = df.columns[0]
year_cols = [c for c in df.columns if c.strip().isdigit()]
key_parts = df[key_col].str.split(",", expand=True)
key_parts.columns = ["freq", "isco08", "age", "sex", "unit", "geo"]
df = pd.concat([key_parts, df.drop(columns=[key_col])], axis=1)
df = df[(df["sex"] == "T") & (df["age"] == "Y15-64")
        & (df["unit"] == "THS_PER")].copy()


def to_num(v):
    if v is None or pd.isna(v):
        return np.nan
    s = str(v).strip()
    if s in ("", ":", "u"):
        return np.nan
    s = s.split()[0]
    try:
        return float(s)
    except ValueError:
        return np.nan


for y in year_cols:
    df[y] = df[y].map(to_num)

years = [y.strip() for y in year_cols]


def isco2_code(c):
    s = str(c).strip()
    if s.startswith("OC") and len(s) == 4 and s[2:].isdigit():
        return s[2:]
    return None


df["isco2"] = df["isco08"].map(isco2_code)
df = df[df["isco2"].notna()].copy()

H_INFO_ISCO2 = {
    "11": +2.0, "12": +1.5, "13": +1.5, "14": +1.0,
    "21": +2.0, "22": +2.0, "23": +1.5, "24": +1.5, "25": +1.0, "26": +2.0,
    "31": +0.5, "32": +0.5, "33":  0.0, "34": +0.5, "35":  0.0,
    "41": -2.0, "42": -1.5, "43": -2.0, "44": -1.5,
    "51":  0.0, "52": -0.5, "53": +0.5, "54":  0.0,
    "61": +0.5, "62": +0.5, "63":  0.0,
    "71": +0.5, "72":  0.0, "73":  0.0, "74": +0.5, "75": -0.5,
    "81": -1.5, "82": -2.0, "83": -0.5,
    "91": -1.5, "92": -1.0, "93": -1.0, "94": -1.5, "95": -1.0, "96": -1.0,
}
df["H_info"] = df["isco2"].map(H_INFO_ISCO2)
df = df.dropna(subset=["H_info"])
print(f"  ISCO 2-digit rows after H_info mapping: {len(df):,}")


def panel_for_period(t0, t1, label):
    """Build country x ISCO panel for a t0 -> t1 5-year window."""
    c0, c1 = year_cols[years.index(t0)], year_cols[years.index(t1)]
    p = df[["geo", "isco2", "H_info", c0, c1]].copy()
    p.columns = ["geo", "isco2", "H_info", "emp_t0", "emp_t1"]
    p = p.dropna(subset=["emp_t0", "emp_t1"])
    p = p[(p["emp_t0"] > 1) & (p["emp_t1"] > 1)]
    n_yrs = int(t1) - int(t0)
    p["delta_ann"] = (p["emp_t1"] / p["emp_t0"]) ** (1 / n_yrs) - 1
    print(f"    {label:18s} ({t0} -> {t1}, {n_yrs}yr): N = {len(p):,}, "
          f"countries = {p['geo'].nunique()}")
    return p


print("\n[2/5] Building two parallel panels (pre and post ChatGPT)...")
pre = panel_for_period("2014", "2019", "PRE  (pre-ChatGPT)")
post = panel_for_period("2019", "2024", "POST (post-ChatGPT)")


def ols(X, y):
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
    return b, se, t, p_two, p_one, r2


def fit_panel(p, label):
    """Spec: delta_ann ~ alpha + beta * H_info + country FE."""
    ones = np.ones(len(p))
    ctry_d = pd.get_dummies(p["geo"], prefix="cty",
                             drop_first=True).astype(float)
    X = np.column_stack([ones, p["H_info"].to_numpy(), ctry_d.to_numpy()])
    y = p["delta_ann"].to_numpy()
    b, se, t, p_two, p_one, r2 = ols(X, y)
    print(f"\n  [{label}] (N = {len(p):,}, country FE)")
    print(f"    beta(H_info) = {b[1]:+.4e}  SE {se[1]:.4e}")
    print(f"    t = {t[1]:+.3f}  p_one = {p_one:.4g}  R^2 = {r2:.4f}")
    return {"beta": float(b[1]), "se": float(se[1]),
            "t": float(t[1]), "p_one": float(p_one),
            "p_two": float(p_two[1]), "R2": float(r2),
            "N": int(len(p))}


print("\n[3/5] Running parallel regressions (country FE)...")
res_pre = fit_panel(pre, "PRE 2014-2019")
res_post = fit_panel(post, "POST 2019-2024")

# Difference test
diff = res_post["beta"] - res_pre["beta"]
diff_se = np.sqrt(res_pre["se"]**2 + res_post["se"]**2)
diff_t = diff / diff_se
diff_p_two = 2 * (1 - stats.t.cdf(np.abs(diff_t),
                                   res_pre["N"] + res_post["N"] - 4))
print(f"\n[4/5] Pre vs Post comparison:")
print(f"  beta_pre  = {res_pre['beta']:+.4e}")
print(f"  beta_post = {res_post['beta']:+.4e}")
print(f"  difference (post - pre) = {diff:+.4e}, SE = {diff_se:.4e}")
print(f"  t = {diff_t:+.3f}, two-sided p = {diff_p_two:.4g}")

# Verdict
if res_pre["t"] < 1.96:
    if res_post["t"] > 3:
        verdict = ("VERDICT (a): beta_pre is NS but beta_post is highly "
                   "significant. H4-info appears genuinely AI-driven "
                   "(post-ChatGPT effect).")
    else:
        verdict = ("Both pre and post are weak; data inconclusive.")
elif diff_p_two > 0.10:
    verdict = ("VERDICT (b): beta_pre and beta_post are both significant "
               "and statistically indistinguishable. H4-info is a deep "
               "long-run routinizability gradient (automation, offshoring, "
               "demographic ageing); AI accelerates rather than singularly "
               "drives it.")
elif res_post["beta"] > res_pre["beta"]:
    verdict = ("VERDICT (a-mixed): pre is significant but post is "
               "significantly larger. H4-info is a long-run gradient "
               "that AI further accelerated post-2022.")
else:
    verdict = ("VERDICT (c): post-period coefficient is SMALLER than "
               "pre-period. Counter to H4-info-AI hypothesis; "
               "alternative explanations needed.")
print(f"\n  {verdict}")

print("\n[5/5] Triple-difference (DDD): H_info x post_dummy")
# Stack pre and post, run interacted regression
pre["post"] = 0
post["post"] = 1
stacked = pd.concat([pre, post], ignore_index=True)
ones = np.ones(len(stacked))
ctry_d = pd.get_dummies(stacked["geo"], prefix="cty",
                         drop_first=True).astype(float)
post_d = stacked["post"].to_numpy()
hinfo = stacked["H_info"].to_numpy()
X = np.column_stack([ones, hinfo, post_d, hinfo * post_d, ctry_d.to_numpy()])
y = stacked["delta_ann"].to_numpy()
n, k = X.shape
b, *_ = np.linalg.lstsq(X, y, rcond=None)
res = y - X @ b
sigma2 = (res ** 2).sum() / (n - k)
cov = sigma2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
t = b / se
p_two = 2 * (1 - stats.t.cdf(np.abs(t), n - k))
p_one = 1 - stats.t.cdf(t[3], n - k)
print(f"  Stacked panel (N={n:,}):")
print(f"    beta(H_info)         = {b[1]:+.4e}  t = {t[1]:+.3f}  p2 = {p_two[1]:.4g}")
print(f"    beta(post)           = {b[2]:+.4e}  t = {t[2]:+.3f}  p2 = {p_two[2]:.4g}")
print(f"    beta(H_info x post)  = {b[3]:+.4e}  t = {t[3]:+.3f}  "
      f"p2 = {p_two[3]:.4g}  p_one(b>0) = {p_one:.4g}")

ddd = {
    "beta_H_info": float(b[1]),
    "beta_post": float(b[2]),
    "beta_interaction": float(b[3]),
    "se_interaction": float(se[3]),
    "t_interaction": float(t[3]),
    "p_two_interaction": float(p_two[3]),
    "p_one_positive_interaction": float(p_one),
    "N": int(n),
}

# Save
out = {
    "v2.8_pretrends": {
        "PRE_2014_2019": res_pre,
        "POST_2019_2024": res_post,
        "diff_post_minus_pre": float(diff),
        "diff_se": float(diff_se),
        "diff_t": float(diff_t),
        "diff_p_two": float(diff_p_two),
        "verdict": verdict,
        "DDD_interaction": ddd,
    },
}
with open(os.path.join(base, "v28_pretrends_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n  Saved -> v28_pretrends_results.json")
