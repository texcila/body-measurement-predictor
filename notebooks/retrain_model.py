# notebooks/retrain_model.py
import sys
import os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor

# Allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fashion_rules import CUSTOM_RULES

def retrain_hybrid_model():
    # Path configuration
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(root_dir, "data", "model_ready_measurements.xlsx")
    model_path = os.path.join(root_dir, "models", "body_measurement_predictor_v5.pkl")
    
    # Create models directory if missing
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    print("📂 Loading dataset...")
    df = pd.read_excel(data_path)

    # Clean and validate data
    measurement_cols = [col for col in df.columns if col.endswith("_cm")]
    df[measurement_cols] = df[measurement_cols].astype(float)
    df = df.dropna(subset=measurement_cols, how='all')

    # Define model inputs/outputs
    input_features = ["height_cm", "bust_cm", "waist_cm", "hip_cm", "chest_cm"]
    target_features = [col for col in measurement_cols if col not in input_features]

    print(f"🤖 Training on {len(df)} samples with {len(target_features)} targets...")
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.1,
        verbosity=1,
        enable_categorical=True
    )
    model.fit(df[input_features], df[target_features])

    # Save hybrid model package
    hybrid_model = {
        "model": model,
        "rules": CUSTOM_RULES,
        "input_features": input_features,
        "target_features": target_features,
        "data_columns": measurement_cols
    }
    joblib.dump(hybrid_model, model_path)
    print(f"✅ Model v5 saved to: {model_path}")

if __name__ == "__main__":
    retrain_hybrid_model()