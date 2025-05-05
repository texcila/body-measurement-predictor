import pandas as pd

# Paths to your files
original_path = "data/original_measurements.xlsx"
relationships_path = "data/measurement_relationships.xlsx"
output_path = "data/cleaned_measurements_filled.xlsx"

# Load the original dataset and rules
df_original = pd.read_excel(original_path)
df_rules = pd.read_excel(relationships_path)

# Make a copy of the original data
df_filled = df_original.copy()

# Apply rules to fill missing values
for idx, row in df_rules.iterrows():
    try:
        target = row["Target"].strip()
        base = row["Base"].strip()
        multiplier = float(row["Multiplier"])

        if target in df_filled.columns and base in df_filled.columns:
            mask = df_filled[target].isna() & df_filled[base].notna()
            df_filled.loc[mask, target] = df_filled.loc[mask, base] * multiplier
    except Exception as e:
        print(f"Skipping rule {idx} due to error: {e}")

# Round all numeric values to 1 decimal place
df_filled = df_filled.round(1)

# Save to new file
df_filled.to_excel(output_path, index=False)
print(f"✅ Cleaned file saved to: {output_path}")
