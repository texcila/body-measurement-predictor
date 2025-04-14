# notebooks/retrain_model.py
import sys
import os
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import joblib

# Allow imports from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fashion_rules import CUSTOM_RULES

# 1. Load data
print("📂 Loading measurements...")
excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "model_ready_measurements.xlsx")
df = pd.read_excel(excel_path)

# 1b. Convert datetime columns to strings to avoid XGBoost error
for col in df.select_dtypes(include=["datetime64"]).columns:
    df[col] = df[col].astype(str)

# 2. Ensure all input columns exist
input_features = ["height_cm", "bust_cm", "waist_cm", "hip_cm", "chest_cm"]
for col in input_features:
    if col not in df.columns:
        df[col] = np.nan

# 3. Apply rules
print("👗 Applying measurement rules...")
for rule_name, rule in CUSTOM_RULES.items():
    try:
        if rule_name not in df.columns:
            continue

        if rule["type"] == "proportion" and rule["base"] in df.columns:
            missing = df[rule_name].isna()
            df.loc[missing, rule_name] = df.loc[missing, rule["base"]] * rule["multiplier"]

        elif rule["type"] == "ratio":
            num, denom = rule["numerator"], rule["denominator"]
            if num in df.columns and denom in df.columns:
                missing = df[rule_name].isna()
                df.loc[missing, rule_name] = df.loc[missing, num] / df.loc[missing, denom]
    except Exception as e:
        print(f"⚠️ Rule error on {rule_name}: {e}")

# 4. Split features
exclude = input_features + ["id", "date_measured", "notes"]
exclude_keywords = ["id", "date", "notes"]
target_features = [
    col for col in df.columns
    if col not in input_features and not any(kw in col.lower() for kw in exclude_keywords)
]


# 5. Train
print("🤖 Training model...")
model = XGBRegressor(n_estimators=200, learning_rate=0.1, enable_categorical=True)
model.fit(df[input_features], df[target_features])

# 6. Save
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "fashion_measurement_predictor_v3.pkl")
joblib.dump(model, model_path)
print("✅ Saved v3 model accepting 1–4 measurements!")
