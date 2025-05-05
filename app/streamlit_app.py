# app/streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# ---------------------------
# 1. PATH CONFIGURATION
# ---------------------------
current_file = Path(__file__).resolve()
root_dir = current_file.parent.parent
model_path = root_dir / "models/body_measurement_predictor_v5.pkl"

# ---------------------------
# 2. LOAD MODEL WITH METADATA
# ---------------------------
try:
    hybrid_model = joblib.load(model_path)
    model = hybrid_model["model"]
    fashion_rules = hybrid_model["rules"]
    input_features = hybrid_model["input_features"]
    target_features = hybrid_model["target_features"]
except Exception as e:
    st.error(f"🚨 Error: {str(e)}")
    st.stop()

# ---------------------------
# 3. UTILITIES
# ---------------------------
def convert_units(value, to_inches):
    return round(float(value)/2.54, 1) if to_inches else round(float(value), 1)

def gentle_rule_adjustment(raw_pred, user_inputs):
    adjusted = raw_pred.copy()
    for measurement, rules in fashion_rules.items():
        if measurement in input_features:
            continue  # Skip user-provided measurements
            
        for rule in rules:
            try:
                if rule["type"] == "proportion" and rule["base"] in user_inputs:
                    base_value = user_inputs[rule["base"]]
                    if not pd.isna(base_value):
                        rule_value = base_value * rule["multiplier"]
                        current = adjusted.get(measurement, rule_value)
                        adjusted[measurement] = (current * 0.8) + (rule_value * 0.2)
            except Exception:
                continue
    return adjusted

# ---------------------------
# 4. STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="Body Measurement AI", layout="centered")
st.title("👗 Body Measurement Predictor")

# Unit toggle
unit = st.selectbox("Measurement Units", ["Centimeters (cm)", "Inches (in)"])
to_inches = unit == "Inches (in)"

# ---------------------------
# 5. USER INPUTS
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
user_input["height_cm"] = round(height * 2.54, 1) if to_inches else height

# Optional measurements
st.subheader("🔍 Additional Measurements (Choose at least 2)")
optional_cols = ["bust_cm", "waist_cm", "hip_cm", "chest_cm"]
selected = st.multiselect(
    "Select measurements to provide",
    options=[col.replace("_cm", "").title() for col in optional_cols],
    max_selections=4
)

# Collect inputs
for measure in selected:
    col_name = measure.lower().replace(" ", "_") + "_cm"
    value = st.number_input(
        f"{measure} ({'in' if to_inches else 'cm'})",
        min_value=0.0,
        max_value=convert_units(200, to_inches),
        value=convert_units(80, to_inches)
    )
    user_input[col_name] = round(value * 2.54, 1) if to_inches else value

# ---------------------------
# 6. PREDICTION & RESULTS
# ---------------------------
if len(selected) >= 2 and st.button("🚀 Predict All Measurements"):
    try:
        # Prepare input
        full_input = {col: np.nan for col in input_features}
        full_input.update(user_input)
        
        # Predict
        input_df = pd.DataFrame([full_input])[input_features]
        raw_pred = model.predict(input_df)[0]
        pred_results = dict(zip(target_features, raw_pred))
        
        # Apply rules to predictions only
        adjusted_preds = gentle_rule_adjustment(pred_results, full_input)
        final_results = {**full_input, **adjusted_preds}
        
        # Display
        st.success("## 📐 Prediction Results")
        display_data = []
        for col in input_features + target_features:
            value = final_results.get(col, np.nan)
            if pd.isna(value):
                continue
                
            display_value = convert_units(value, to_inches)
            display_data.append({
                "Measurement": col.replace("_cm", "").replace("_", " ").title(),
                "Value": f"{display_value:.1f} {'in' if to_inches else 'cm'}",
                "Type": "Provided" if col in user_input else "Predicted"
            })
        
        st.dataframe(
            pd.DataFrame(display_data),
            column_config={
                "Measurement": "Body Part",
                "Value": "Measurement",
                "Type": st.column_config.SelectboxColumn(
                    "Source",
                    options=["Provided", "Predicted"]
                )
            },
            hide_index=True,
            use_container_width=True,
            height=600
        )

        # Detailed analysis
        with st.expander("📊 Body Proportions"):
            if "waist_cm" in final_results and "hip_cm" in final_results:
                ratio = final_results["hip_cm"] / final_results["waist_cm"]
                st.metric("Waist-Hip Ratio", 
                         f"{ratio:.2f} (Ideal: 0.7-0.8)",
                         help="Healthy range for women")
                
            for col in ["bust_cm", "waist_cm", "hip_cm"]:
                if col in final_results:
                    value = final_results[col]
                    min_val = 50 if "bust" in col else 40
                    max_val = 200 if "hip" in col else 180
                    progress = (value - min_val) / (max_val - min_val)
                    st.write(f"**{col.replace('_cm', '').title()}:**")
                    st.progress(float(np.clip(progress, 0.0, 1.0)))
                    st.caption(f"{convert_units(value, to_inches):.1f} {'in' if to_inches else 'cm'}")

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
elif len(selected) < 2:
    st.warning("⚠️ Please select at least 2 additional measurements!")