"""
v2.7 - ISCO 2-digit cross-country panel + Eurostat GenAI-usage interaction.

Builds on v2.6 by:
  (a) replacing ISCO 1-digit (10 categories) with ISCO 2-digit
      (~40 detailed categories), giving more variation in H_info.
  (b) adding country-level GenAI usage rate (Eurostat 2025 ICT survey
      via Our World in Data) as a country-level AI-adoption instrument.
  (c) testing a country x occupation interaction:
      delta_emp ~ H_info_ISCO2 + GenAI_country + (H_info x GenAI) + FE.

The interaction tests whether the H4-info effect is *stronger* in
countries with higher actual GenAI usage --- the most demanding causal
test so far.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
tsv = os.path.join(base, "data/eurostat_lfsa_egai2d.tsv")
genai_csv = os.path.join(base, "data/eurostat_genai_usage.csv")

print("[1/7] Parsing Eurostat ISCO panel...")
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
y2019 = year_cols[years.index("2019")]
y2024 = year_cols[years.index("2024")]


# ISCO 2-digit codes are OC11..OC96
def isco2_code(c):
    s = str(c).strip()
    if s.startswith("OC") and len(s) == 4 and s[2:].isdigit():
        return s[2:]
    return None


df["isco2"] = df["isco08"].map(isco2_code)
df2 = df[df["isco2"].notna()].copy()
print(f"  ISCO 2-digit rows: {len(df2):,}, unique codes: "
      f"{df2['isco2'].nunique()}")

print("[2/7] Manual H_info mapping for 38 ISCO 2-digit categories "
      "(Acemoglu-Autor 2011 inspired, AI-data-free)...")
H_INFO_ISCO2 = {
    # Managers (1x)
    "11": +2.0, "12": +1.5, "13": +1.5, "14": +1.0,
    # Professionals (2x)
    "21": +2.0, "22": +2.0, "23": +1.5, "24": +1.5, "25": +1.0, "26": +2.0,
    # Technicians (3x)
    "31": +0.5, "32": +0.5, "33":  0.0, "34": +0.5, "35":  0.0,
    # Clerical (4x) -- routine cognitive
    "41": -2.0, "42": -1.5, "43": -2.0, "44": -1.5,
    # Services & sales (5x) -- mixed
    "51":  0.0, "52": -0.5, "53": +0.5, "54":  0.0,
    # Skilled agricultural (6x)
    "61": +0.5, "62": +0.5, "63":  0.0,
    # Craft (7x) -- mixed manual
    "71": +0.5, "72":  0.0, "73":  0.0, "74": +0.5, "75": -0.5,
    # Plant ops (8x) -- routine manual
    "81": -1.5, "82": -2.0, "83": -0.5,
    # Elementary (9x) -- routine manual
    "91": -1.5, "92": -1.0, "93": -1.0, "94": -1.5, "95": -1.0, "96": -1.0,
    # Armed forces 0x -- exclude
}
df2["H_info"] = df2["isco2"].map(H_INFO_ISCO2)
df2 = df2.dropna(subset=["H_info"])
print(f"  After mapping: {df2['isco2'].nunique()} ISCO 2-digit categories")

print("[3/7] Building country x ISCO panel for 2019 vs 2024...")
panel = df2[["geo", "isco2", "H_info", y2019, y2024]].copy()
panel.columns = ["geo", "isco2", "H_info", "emp_2019", "emp_2024"]
panel = panel.dropna(subset=["emp_2019", "emp_2024"])
panel = panel[(panel["emp_2019"] > 1) & (panel["emp_2024"] > 1)]
panel["delta_emp_ann"] = (panel["emp_2024"] / panel["emp_2019"]) ** (1/5) - 1
print(f"  Panel: N = {len(panel):,}, countries = "
      f"{panel['geo'].nunique()}, ISCO 2-digit = {panel['isco2'].nunique()}")

print("[4/7] Loading GenAI usage by country (Eurostat 2025)...")
gen = pd.read_csv(genai_csv)
gen.columns = ["country_name", "code3", "year", "genai_usage"]
# Map country code (3-letter ISO) to 2-letter Eurostat geo
ISO3_TO_GEO = {
    "AUT": "AT", "BEL": "BE", "BIH": "BA", "BGR": "BG", "HRV": "HR",
    "CYP": "CY", "CZE": "CZ", "DNK": "DK", "EST": "EE", "FIN": "FI",
    "FRA": "FR", "DEU": "DE", "GRC": "EL", "HUN": "HU", "ISL": "IS",
    "IRL": "IE", "ITA": "IT", "LVA": "LV", "LTU": "LT", "LUX": "LU",
    "MLT": "MT", "MNE": "ME", "NLD": "NL", "MKD": "MK", "NOR": "NO",
    "POL": "PL", "PRT": "PT", "ROU": "RO", "SRB": "RS", "SVK": "SK",
    "SVN": "SI", "ESP": "ES", "SWE": "SE", "CHE": "CH", "TUR": "TR",
    "GBR": "UK",
}
gen["geo"] = gen["code3"].map(ISO3_TO_GEO)
gen = gen.dropna(subset=["geo"])
print(f"  GenAI countries: {len(gen)}, mean usage = "
      f"{gen['genai_usage'].mean():.1f}%")

panel = panel.merge(gen[["geo", "genai_usage"]], on="geo", how="inner")
panel["z_genai"] = stats.zscore(panel["genai_usage"])
print(f"  Merged with GenAI: N = {len(panel):,}, "
      f"countries = {panel['geo'].nunique()}")

print("\n[5/7] v2.7 Regressions:")

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


y = panel["delta_emp_ann"].to_numpy()
ones = np.ones(len(panel))

# Spec 1: H_info only on ISCO 2-digit panel
X1 = np.column_stack([ones, panel["H_info"].to_numpy()])
b1, se1, t1, p_two1, p_one1, r2_1 = ols(X1, y)
print(f"\n[Spec 1] delta_emp_ann ~ alpha + beta * H_info_ISCO2 (no FE)")
print(f"  N = {len(panel):,}")
print(f"  beta(H_info) = {b1[1]:+.4e}  SE {se1[1]:.4e}  "
      f"t = {t1[1]:+.3f}  p_one = {p_one1:.4g}  R^2 = {r2_1:.4f}")

# Spec 2: + country FE
ctry_d = pd.get_dummies(panel["geo"], prefix="cty", drop_first=True).astype(float)
X2 = np.column_stack([ones, panel["H_info"].to_numpy(), ctry_d.to_numpy()])
b2, se2, t2, p_two2, p_one2, r2_2 = ols(X2, y)
print(f"\n[Spec 2] + country FE")
print(f"  beta(H_info) = {b2[1]:+.4e}  SE {se2[1]:.4e}  "
      f"t = {t2[1]:+.3f}  p_one = {p_one2:.4g}  R^2 = {r2_2:.4f}")

# Spec 3: + GenAI usage main effect (no interaction yet)
X3 = np.column_stack([ones, panel["H_info"].to_numpy(),
                      panel["z_genai"].to_numpy()])
b3, se3, t3, p_two3, p_one3, r2_3 = ols(X3, y)
print(f"\n[Spec 3] + GenAI usage main effect (no FE, additive)")
print(f"  beta(H_info)    = {b3[1]:+.4e}  t = {t3[1]:+.3f}  p_one = {p_one3:.4g}")
print(f"  beta(z_genai)   = {b3[2]:+.4e}  t = {t3[2]:+.3f}  p2 = {p_two3[2]:.4g}")
print(f"  R^2 = {r2_3:.4f}")

# Spec 4: KEY -- H_info x GenAI interaction
panel["interaction"] = panel["H_info"] * panel["z_genai"]
X4 = np.column_stack([ones, panel["H_info"].to_numpy(),
                      panel["z_genai"].to_numpy(),
                      panel["interaction"].to_numpy()])
b4, se4, t4, p_two4, _, r2_4 = ols(X4, y)
p_one_int = 1 - stats.t.cdf(t4[3], len(panel) - 4)
print(f"\n[Spec 4 KEY] + H_info x GenAI INTERACTION")
print(f"  beta(H_info)        = {b4[1]:+.4e}  t = {t4[1]:+.3f}  p2 = {p_two4[1]:.4g}")
print(f"  beta(z_genai)       = {b4[2]:+.4e}  t = {t4[2]:+.3f}  p2 = {p_two4[2]:.4g}")
print(f"  beta(INTERACTION)   = {b4[3]:+.4e}  t = {t4[3]:+.3f}  "
      f"p2 = {p_two4[3]:.4g}  p_one(b>0) = {p_one_int:.4g}")
print(f"  R^2 = {r2_4:.4f}")

# Spec 5: full model with country FE + interaction
X5 = np.column_stack([ones, panel["H_info"].to_numpy(),
                      panel["interaction"].to_numpy(),
                      ctry_d.to_numpy()])
b5, se5, t5, p_two5, _, r2_5 = ols(X5, y)
p_one5_int = 1 - stats.t.cdf(t5[2], len(panel) - X5.shape[1])
print(f"\n[Spec 5 FULL] + country FE + H_info x GenAI interaction")
print(f"  beta(H_info)        = {b5[1]:+.4e}  t = {t5[1]:+.3f}  p2 = {p_two5[1]:.4g}")
print(f"  beta(INTERACTION)   = {b5[2]:+.4e}  t = {t5[2]:+.3f}  "
      f"p2 = {p_two5[2]:.4g}  p_one(b>0) = {p_one5_int:.4g}")
print(f"  R^2 = {r2_5:.4f}")

print("\n[6/7] Sub-sample: H_info effect in high-GenAI vs low-GenAI countries")
median = panel["genai_usage"].median()
hi = panel[panel["genai_usage"] >= median]
lo = panel[panel["genai_usage"] < median]


def beta_h(p, label):
    X = np.column_stack([np.ones(len(p)), p["H_info"].to_numpy()])
    yy = p["delta_emp_ann"].to_numpy()
    b, *_ = np.linalg.lstsq(X, yy, rcond=None)
    res = yy - X @ b
    se_ = np.sqrt(((res**2).sum()/(len(p)-2)) * np.linalg.inv(X.T@X)[1,1])
    t = b[1]/se_
    p_one = 1 - stats.t.cdf(t, len(p)-2)
    print(f"  {label} (N={len(p)}): beta = {b[1]:+.4e}  t = {t:+.3f}  p_one = {p_one:.4g}")
    return float(b[1]), float(se_), float(t), float(p_one)


b_hi, se_hi, t_hi, p_hi = beta_h(hi, "High-GenAI countries (>= median)")
b_lo, se_lo, t_lo, p_lo = beta_h(lo, "Low-GenAI countries  (<  median)")
diff = b_hi - b_lo
diff_se = np.sqrt(se_hi**2 + se_lo**2)
diff_t = diff / diff_se
diff_p = 1 - stats.t.cdf(diff_t, len(hi) + len(lo) - 4)
print(f"\n  Difference (high - low) = {diff:+.4e}, t = {diff_t:+.3f}, "
      f"one-sided p = {diff_p:.4g}")

# Save
out = {
    "v2.7_ISCO2_GenAI": {
        "N": int(len(panel)), "n_countries": int(panel["geo"].nunique()),
        "n_isco2": int(panel["isco2"].nunique()),
        "spec_1_no_FE": {"beta": float(b1[1]), "t": float(t1[1]),
                         "p_one": float(p_one1), "R2": float(r2_1)},
        "spec_2_country_FE": {"beta": float(b2[1]), "t": float(t2[1]),
                              "p_one": float(p_one2), "R2": float(r2_2)},
        "spec_3_genai_main": {"beta_H_info": float(b3[1]),
                              "beta_genai": float(b3[2]),
                              "p_genai_two": float(p_two3[2]), "R2": float(r2_3)},
        "spec_4_interaction": {"beta_H_info": float(b4[1]),
                               "beta_interaction": float(b4[3]),
                               "p_two_int": float(p_two4[3]),
                               "p_one_int": float(p_one_int), "R2": float(r2_4)},
        "spec_5_full": {"beta_H_info": float(b5[1]),
                        "beta_interaction": float(b5[2]),
                        "p_two_int": float(p_two5[2]),
                        "p_one_int": float(p_one5_int), "R2": float(r2_5)},
        "subsample_split": {
            "high_GenAI": {"beta": b_hi, "t": t_hi, "p_one": p_hi},
            "low_GenAI": {"beta": b_lo, "t": t_lo, "p_one": p_lo},
            "diff": diff, "diff_t": diff_t, "diff_p_one": diff_p,
        },
    },
}
with open(os.path.join(base, "v27_isco2_genai_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[7/7] Saved -> v27_isco2_genai_results.json")
