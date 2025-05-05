import pandas as pd
import numpy as np
import re

# Load your original dataset
df = pd.read_excel('data/original_measurements.xlsx')

# List of rules extracted from your image (simplified to formula and columns)
rules = [
    ("waist_cm", "0.7 * hip_cm"),
    ("pant_inseam_cm", "0.5 * height_cm"),
    ("bust_height_cm", "2.0 * bust_radius_cm"),
    ("dress_knee_length_cm", "front_waist_length_cm + skirt_knee_length_cm"),
    ("dress_full_length_cm", "front_waist_length_cm + skirt_full_length_cm"),
    ("around_neck_cm", "0.37 * waist_cm"),
    ("around_thigh_cm", "0.6 * hip_cm"),
    ("front_waist_length_cm", "0.26 * height_cm"),
    ("around_bicep_cm", "0.25 * bust_cm"),
    ("waist_cm", "0.43 * height_cm"),
    ("pant_body_rise_cm", "pant_outseam_cm - pant_inseam_cm"),
    ("around_knee_cm", "0.5 * hip_cm"),
    ("elbow_length_cm", "sleeve_length_cm - 0.2 * height_cm"),
    ("around_elbow_cm", "0.08 * height_cm"),
    ("skirt_knee_length_cm", "0.4 * height_cm"),
    ("around_calf_cm", "0.7 * around_thigh_cm"),
    ("height_cm", "6.5 * back_shoulder_cm"),
    ("around_elbow_cm", "0.85 * around_bicep_cm"),
    ("waist_cm", "0.35 * pant_inseam_cm"),
    ("skirt_full_length_cm", "0.5 * height_cm"),
    ("elbow_length_cm", "0.25 * height_cm"),
    ("bust_cm", "1.5 * waist_cm"),
    ("around_thigh_cm", "0.35 * height_cm"),
    ("chest_cm", "10 + waist_cm"),
    ("bust_height_cm", "0.6 * bust_cm"),
    ("around_thigh_cm", "1.5 * around_calf_cm"),
    ("pant_body_rise_cm", "0.35 * waist_cm"),
    ("breast_distance_cm", "0.5 * bust_cm"),
    ("bust_height_cm", "0.3 * height_cm"),
    ("hip_cm", "2 * around_knee_cm"),
    ("around_wrist_cm", "0.05 * height_cm"),
    ("around_ankle_cm", "0.6 * around_calf_cm"),
    ("around_armhole_cm", "0.3 * bust_cm"),
    ("around_neck_cm", "0.4 * chest_cm"),
    ("around_ankle_cm", "0.5 * around_thigh_cm"),
    ("around_knee_cm", "1.5 * around_ankle_cm"),
    ("around_wrist_cm", "1.1 * around_ankle_cm"),
    ("front_waist_length_cm", "1.3 * bust_height_cm"),
    ("waist_cm", "2.5 * waist_hip_distance_cm"),
    ("front_waist_length_cm", "0.4 * height_cm"),
]

# Fill missing values using the rules
for target, formula in rules:
    if target not in df.columns:
        continue
    missing_rows = df[target].isna()

    # Attempt to evaluate the formula only if all base columns exist
    try:
        # Extract base columns used in formula
        base_columns = re.findall(r'[a-zA-Z_]+_cm', formula)
        if all(col in df.columns for col in base_columns):
            # Evaluate the formula row-wise
            df.loc[missing_rows, target] = df.loc[missing_rows].eval(formula)
    except Exception as e:
        print(f"Skipping rule: {target} = {formula} due to error: {e}")

# Round all values to 1 decimal place
df = df.round(1)

# Save the cleaned and filled dataset
output_path = 'data/cleaned_filled_measurements.xlsx'
df.to_excel(output_path, index=False)
print(f"✅ Cleaned file saved to: {output_path}")
