# check_columns.py (place in project root folder)
import sys
import os
import pandas as pd
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from fashion_rules import CUSTOM_RULES

# Load data
excel_path = current_dir / "data/model_ready_measurements.xlsx"
df = pd.read_excel(excel_path)

# Compare columns
rule_cols = set(CUSTOM_RULES.keys())
data_cols = set(df.columns)

print("\n🔍 Column Analysis:")
print("Missing in data:", rule_cols - data_cols)
print("Extra in data:", data_cols - rule_cols)
print("Matching columns:", len(rule_cols & data_cols))