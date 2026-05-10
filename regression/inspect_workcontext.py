"""Identify all physical-demand elements in O*NET Work Context."""
import os
import pandas as pd

base = os.path.expanduser("~/Desktop/entropy-ai-paper/regression")
wc = pd.read_excel(os.path.join(base, "data/onet/db_30_2_excel/Work Context.xlsx"))
elems = wc[["Element ID", "Element Name"]].drop_duplicates().sort_values("Element ID")
print("All Work Context elements (Element ID + Name):")
print(elems.to_string(index=False))
print(f"\nTotal: {len(elems)} elements")

# Filter for physical
physical = elems[elems["Element ID"].str.startswith("4.C.2")]
print(f"\n4.C.2.* elements ({len(physical)}):")
print(physical.to_string(index=False))
