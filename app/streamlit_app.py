# app/streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

# ---------------------------
# 1. PATH CONFIGURATION
# ---------------------------
current_file = Path(__file__).resolve()
root_dir = current_file.parent.parent
model_path = root_dir / "models/fashion_measurement_predictor_v3.pkl"
metadata_path = root_dir / "data/metadata.json"

# ---------------------------
# 2. LOAD RESOURCES
# ---------------------------
try:
    model = joblib.load(model_path)
    with open(metadata_path) as f:
        metadata = json.load(f)
except Exception as e:
    st.error(f"🚨 Error loading resources: {str(e)}")
    st.stop()

# ---------------------------
# 3. MEASUREMENT CONFIGURATION
# ---------------------------
MEASUREMENT_RULES = {
    "hip_cm": {"base": "waist_cm", "multiplier": 1.2},
    "chest_cm": {"base": "bust_cm", "multiplier": 0.95}
}

MEASUREMENT_LIMITS_CM = {
    "height_cm": (100, 250),
    "bust_cm": (60, 200),
    "waist_cm": (50, 150),
    "hip_cm": (70, 200),
    "chest_cm": (55, 150)
}

# ---------------------------
# 4. UTILITY FUNCTIONS
# ---------------------------
def convert_units(value, to_inches):
    """Convert between cm and inches"""
    return round(value / 2.54, 1) if to_inches else round(value, 1)

def apply_fashion_rules(inputs):
    """Fill missing measurements using proportional rules"""
    processed = inputs.copy()
    
    # Hip from Waist
    if pd.isna(processed.get("hip_cm")) and "waist_cm" in processed:
        processed["hip_cm"] = processed["waist_cm"] * 1.2
        
    # Chest from Bust
    if pd.isna(processed.get("chest_cm")) and "bust_cm" in processed:
        processed["chest_cm"] = processed["bust_cm"] * 0.95
        
    return processed

# ---------------------------
# 5. STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="Fashion Measurement AI", layout="centered")
st.title("👗 Body Measurement Predictor")

# Unit selection
unit = st.selectbox("Measurement Units", ["Centimeters (cm)", "Inches (in)"])
to_inches = unit == "Inches (in)"

# ---------------------------
# 6. USER INPUTS
# ---------------------------
st.subheader("📏 Required Measurements")
user_input = {}

# Height (always required)
height = st.number_input(
    f"Height ({'in' if to_inches else 'cm'})",
    min_value=convert_units(100, to_inches),
    max_value=convert_units(250, to_inches),
    value=convert_units(165, to_inches)
)
user_input["height_cm"] = height * 2.54 if to_inches else height

# Optional measurements
st.subheader("🔍 Additional Measurements (Choose at least 2)")
optional_cols = ["bust_cm", "waist_cm", "hip_cm", "chest_cm"]
selected = st.multiselect(
    "Select measurements to provide",
    options=[col.replace("_cm", "").title() for col in optional_cols],
    max_selections=4
)

# Collect selected measurements
for measure in selected:
    col_name = measure.lower().replace(" ", "_") + "_cm"
    display_min = convert_units(MEASUREMENT_LIMITS_CM[col_name][0], to_inches)
    display_max = convert_units(MEASUREMENT_LIMITS_CM[col_name][1], to_inches)
    
    value = st.number_input(
        f"{measure} ({'in' if to_inches else 'cm'})",
        min_value=float(display_min),
        max_value=float(display_max),
        value=float(display_min)
    )
    user_input[col_name] = value * 2.54 if to_inches else value

# ---------------------------
# 7. PREDICTION & VALIDATION
# ---------------------------
if len(selected) >= 2:
    try:
        # Apply fashion rules to missing measurements
        processed_inputs = apply_fashion_rules(user_input)
        
        # Create model input with correct feature order
        model_input = {col: np.nan for col in model.feature_names_in_}
        for col, value in processed_inputs.items():
            if col in model_input:
                model_input[col] = value
                
        input_df = pd.DataFrame([model_input])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        results = dict(zip(metadata["target_cols"], prediction))
        
        # ---------------------------
        # 8. DISPLAY RESULTS
        # ---------------------------
        st.success("## 📐 Prediction Results")
        
        # Convert results to display units
        display_results = {
            k: convert_units(v, to_inches) 
            for k, v in results.items()
        }
        
        # Main measurements
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔑 Key Measurements")
            for measure in ["inseam_cm", "shoulder_width_cm", "arm_length_cm"]:
                if measure in display_results:
                    st.metric(
                        measure.replace("_cm", "").title(),
                        f"{display_results[measure]:.1f} {'in' if to_inches else 'cm'}"
                    )
                    
        with col2:
            st.markdown("### 📏 Proportions")
            for measure in ["bust_waist_ratio", "hip_height_ratio"]:
                if measure in display_results:
                    st.metric(
                        measure.replace("_", " ").title(),
                        f"{display_results[measure]:.2f}"
                    )
        
        # Full results expander
        with st.expander("📋 All Technical Measurements"):
            for measure, value in display_results.items():
                st.write(f"**{measure.replace('_cm', '').replace('_', ' ').title()}:**")
                st.progress(value/200 if 'cm' in measure else value)
                st.write(f"{value:.1f} {'in' if to_inches else 'cm'}")
                
    except Exception as e:
        st.error(f"⚠️ Prediction Error: {str(e)}")
else:
    st.warning("⚠️ Please select at least 2 additional measurements!")