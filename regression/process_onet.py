"""
Process O*NET 30.2 Work Activities to derive E^human (J/h) per SOC code.

Method:
  1. Read Work Activities.xlsx, filter element 4.A.3.b.1
     ("Performing General Physical Activities"), Level (LV) scale.
  2. Aggregate O*NET-SOC (8-digit) to BLS-SOC (6-digit) by mean.
  3. Map Level 1-5 to MET via linear: MET = 0.7 + 0.7 * Level.
       Level 1 -> 1.4 MET (sedentary)
       Level 5 -> 4.2 MET (heavy manual)
  4. MET -> J/h assuming 70 kg body mass: E_h = MET * 70 * 4184.
  5. Save CSV for joining with BLS data.
"""
import os
import pandas as pd

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
onet = os.path.join(base, "data", "onet", "db_30_2_excel")

wa = pd.read_excel(os.path.join(onet, "Work Activities.xlsx"))
print("Columns:", wa.columns.tolist())

phys = wa[(wa["Element ID"] == "4.A.3.b.1") & (wa["Scale ID"] == "IM")].copy()
print(f"Rows for 'Performing General Physical Activities' (Importance): {len(phys)}")

# O*NET-SOC code is 8-digit "XX-YYYY.ZZ"; collapse to BLS 6-digit "XX-YYYY"
phys["soc"] = phys["O*NET-SOC Code"].str[:7]
agg = phys.groupby("soc")["Data Value"].mean().reset_index()
agg.columns = ["soc", "physical_level"]

# Importance (1-5) -> MET -> J/h
# IM 1 (not important) ~ 1.2 MET (sedentary), IM 5 (extreme) ~ 4.5 MET (heavy)
# Linear: MET = 0.375 + 0.825 * IM
agg["MET"] = 0.375 + 0.825 * agg["physical_level"]
agg["E_human_J_per_h"] = agg["MET"] * 70.0 * 4184.0   # 70 kg, 4184 J/kcal

print(f"\nN BLS-SOC codes: {len(agg)}")
print("\nphysical_level (1-5) summary:")
print(agg["physical_level"].describe())
print("\nE_human (J/h) summary:")
print(agg["E_human_J_per_h"].describe())

# Top / bottom 5 occupations by physical demand
print("\nTop 5 (most physical):")
top = agg.nlargest(5, "E_human_J_per_h")
print(top.to_string(index=False))
print("\nBottom 5 (least physical):")
bot = agg.nsmallest(5, "E_human_J_per_h")
print(bot.to_string(index=False))

out = os.path.join(base, "e_human_by_soc.csv")
agg.to_csv(out, index=False)
print(f"\nSaved -> {out}")
