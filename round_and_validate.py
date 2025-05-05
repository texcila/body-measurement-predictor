# round_and_validate.py
import pandas as pd

# 1. Load cleaned data
input_path = r"C:\Users\User\Documents\my_project\body-measurement-predictor\data\cleaned_measurements.xlsx"
output_path = r"C:\Users\User\Documents\my_project\body-measurement-predictor\data\rounded_measurements.xlsx"

df = pd.read_excel(input_path)

# 2. Round all numeric columns to 1 decimal place
numeric_cols = df.select_dtypes(include=['number']).columns
df[numeric_cols] = df[numeric_cols].round(1)

# 3. Basic outlier check (customize these ranges as needed)
outlier_checks = {
    'height_cm': (100, 250),
    'waist_cm': (50, 200),
    'hip_cm': (70, 250)
}

# 4. Find potential outliers
outliers = pd.DataFrame()

for col, (min_val, max_val) in outlier_checks.items():
    col_outliers = df[(df[col] < min_val) | (df[col] > max_val)]
    if not col_outliers.empty:
        outliers = pd.concat([outliers, col_outliers])

# 5. Save results
df.to_excel(output_path, index=False)

if not outliers.empty:
    print("⚠️ POTENTIAL OUTLIERS FOUND ⚠️")
    print("Review these rows in your rounded file:")
    print(outliers[['id'] + list(outlier_checks.keys())])
else:
    print("✅ No obvious outliers detected")

print(f"\nRounded data saved to: {output_path}")
print("Please manually verify values in the Excel file")