# clean_data.py
import pandas as pd
import numpy as np

def load_data():
    input_path = r"C:\Users\User\Documents\my_project\body-measurement-predictor\data\original_measurements.xlsx"
    data = pd.read_excel(input_path)
    data["Date Measured (YYYY-MM-DD)"] = pd.to_datetime(data["Date Measured (YYYY-MM-DD)"])
    return data.sort_values(by=["id", "Date Measured (YYYY-MM-DD)"])

def fill_historical(data):
    stable_cols = ["height_cm", "elbow_length_cm", "around_bicep_cm", "around_elbow_cm"]
    for col in stable_cols:
        data[col] = data.groupby("id")[col].transform(lambda x: x.fillna(x.mean()))
    
    time_sensitive_cols = ["waist_cm", "hip_cm", "bust_cm"]
    for col in time_sensitive_cols:
        data[col] = data.groupby("id")[col].ffill()
    return data

def apply_fashion_rules(data):
    rules = {
        # Height Rules
        "height_cm": [
            {"formula": lambda row: row["front_waist_length_cm"] / 0.26, "inputs": ["front_waist_length_cm"], "priority": 1},
            {"formula": lambda row: row["skirt_knee_length_cm"] / 0.4, "inputs": ["skirt_knee_length_cm"], "priority": 2},
            {"formula": lambda row: row["around_thigh_cm"] / 0.4, "inputs": ["around_thigh_cm"], "priority": 3}
        ],
        
        # Upper Body Rules
        "shoulder_underbust_distance_cm": [
            {"formula": lambda row: row["bust_height_cm"] + row["bust_radius_cm"], "inputs": ["bust_height_cm", "bust_radius_cm"], "priority": 1}
        ],
        
        # Arm Measurements
        "around_elbow_cm": [
            {"formula": lambda row: 0.85 * row["around_bicep_cm"], "inputs": ["around_bicep_cm"], "priority": 1}
        ],
        "around_bicep_cm": [
            {"formula": lambda row: row["around_elbow_cm"] / 0.85, "inputs": ["around_elbow_cm"], "priority": 1}
        ],
        
        # Wrist/Hand Rules
        "around_wrist_cm": [
            {"formula": lambda row: 0.85 * row["hand_entry_cm"], "inputs": ["hand_entry_cm"], "priority": 1}
        ],
        "hand_entry_cm": [
            {"formula": lambda row: row["around_wrist_cm"] / 0.85, "inputs": ["around_wrist_cm"], "priority": 1}
        ],
        
        # Dress/Elbow Rules
        "elbow_length_cm": [
            {"formula": lambda row: 0.23 * row["height_cm"], "inputs": ["height_cm"], "priority": 1}
        ],
        "dress_knee_length_cm": [
            {"formula": lambda row: row["front_waist_length_cm"] + row["skirt_knee_length_cm"], "inputs": ["front_waist_length_cm", "skirt_knee_length_cm"], "priority": 1}
        ],
        
        # Full Length Rules
        "dress_full_length_cm": [
            {"formula": lambda row: 0.9 * row["height_cm"], "inputs": ["height_cm"], "priority": 1},
            {"formula": lambda row: row["front_waist_length_cm"] + row["skirt_full_length_cm"], "inputs": ["front_waist_length_cm", "skirt_full_length_cm"], "priority": 2}
        ],
        
        # Skirt Rules
        "skirt_knee_length_cm": [
            {"formula": lambda row: 0.4 * row["height_cm"], "inputs": ["height_cm"], "priority": 1},
            {"formula": lambda row: 0.6 * row["skirt_full_length_cm"], "inputs": ["skirt_full_length_cm"], "priority": 2}
        ],
        "skirt_full_length_cm": [
            {"formula": lambda row: 0.67 * row["height_cm"], "inputs": ["height_cm"], "priority": 1},
            {"formula": lambda row: row["skirt_knee_length_cm"] / 0.6, "inputs": ["skirt_knee_length_cm"], "priority": 2}
        ],
        
        # Flare/Walking Rules
        "flare_out_cm": [
            {"formula": lambda row: row["skirt_knee_length_cm"] - 8, "inputs": ["skirt_knee_length_cm"], "priority": 1}
        ],
        "walking_step_cm": [
            {"formula": lambda row: row["hip_cm"] - 5, "inputs": ["hip_cm"], "priority": 1}
        ],
        
        # Pants Rules
        "pant_waist_cm": [
            {"formula": lambda row: row["waist_cm"] * 1, "inputs": ["waist_cm"], "priority": 1}
        ],
        "pant_hip_cm": [
            {"formula": lambda row: row["hip_cm"] * 1, "inputs": ["hip_cm"], "priority": 1}
        ],
        "pant_waist_hip_seam_cm": [
            {"formula": lambda row: row["waist_hip_distance_cm"] * 1, "inputs": ["waist_hip_distance_cm"], "priority": 1}
        ],
        "pant_body_rise_cm": [
            {"formula": lambda row: 0.35 * row["waist_cm"], "inputs": ["waist_cm"], "priority": 1},
            {"formula": lambda row: row["pant_outseam_cm"] - row["pant_inseam_cm"], "inputs": ["pant_outseam_cm", "pant_inseam_cm"], "priority": 2}
        ],
        "pant_outseam_cm": [
            {"formula": lambda row: row["pant_ankle_length_cm"] * 1, "inputs": ["pant_ankle_length_cm"], "priority": 1},
            {"formula": lambda row: row["pant_inseam_cm"] + row["pant_body_rise_cm"], "inputs": ["pant_inseam_cm", "pant_body_rise_cm"], "priority": 2}
        ],
        "pant_inseam_cm": [
            {"formula": lambda row: row["pant_outseam_cm"] - row["pant_body_rise_cm"], "inputs": ["pant_outseam_cm", "pant_body_rise_cm"], "priority": 1}
        ],
        "pant_full_length_cm": [
            {"formula": lambda row: row["skirt_full_length_cm"] * 1, "inputs": ["skirt_full_length_cm"], "priority": 1}
        ],
        
        # Leg Measurements
        "around_thigh_cm": [
            {"formula": lambda row: 0.45 * row["height_cm"], "inputs": ["height_cm"], "priority": 1},
            {"formula": lambda row: 0.6 * row["hip_cm"], "inputs": ["hip_cm"], "priority": 2}
        ],
        "around_knee_cm": [
            {"formula": lambda row: 0.65 * row["around_thigh_cm"], "inputs": ["around_thigh_cm"], "priority": 1},
            {"formula": lambda row: 1.5 * row["around_ankle_cm"], "inputs": ["around_ankle_cm"], "priority": 2}
        ],
        "around_calf_cm": [
            {"formula": lambda row: row["around_thigh_cm"] / 1.7, "inputs": ["around_thigh_cm"], "priority": 1}
        ],
        "around_ankle_cm": [
            {"formula": lambda row: 0.5 * row["around_thigh_cm"], "inputs": ["around_thigh_cm"], "priority": 1}
        ]
    }

    for target_col in rules:
        sorted_rules = sorted(rules[target_col], key=lambda x: x["priority"])
        for index, row in data.iterrows():
            if pd.isnull(row[target_col]):
                for rule in sorted_rules:
                    if all(not pd.isnull(row[col]) for col in rule["inputs"]):
                        data.at[index, target_col] = rule["formula"](row)
                        break
    return data

def final_cleanup(data):
    for col in data.columns:
        if data[col].isnull().sum() > 0:
            data[col] = data[col].fillna(data[col].median())
    return data

def validate_data(data):
    invalid_heights = data[(data["height_cm"] < 100) | (data["height_cm"] > 250)]
    if not invalid_heights.empty:
        print("ALERT: Impossible heights detected!\n", invalid_heights[["id", "height_cm"]])
    return data

def save_data(data):
    output_path = r"C:\Users\User\Documents\my_project\body-measurement-predictor\data\cleaned_measurements.xlsx"
    data.to_excel(output_path, index=False)
    print(f"✅ Cleaned data saved to: {output_path}")

def main():
    data = load_data()
    data = fill_historical(data)
    data = apply_fashion_rules(data)
    data = final_cleanup(data)
    validate_data(data)
    save_data(data)

if __name__ == "__main__":
    main()