import pandas as pd

# Load the original Excel file
input_file = "data/augmented_measurements_v1.xlsx"
output_file = "data/augmented_measurements_rounded.xlsx"

# Read the Excel file
df = pd.read_excel(input_file)

# Round all numeric columns to 1 decimal place
df_rounded = df.copy()
df_rounded[df_rounded.select_dtypes(include=['float', 'int']).columns] = (
    df_rounded.select_dtypes(include=['float', 'int']).round(1)
)

# Save the new file
df_rounded.to_excel(output_file, index=False)

print(f"✅ Rounded file saved as: {output_file}")
