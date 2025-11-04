import pandas as pd

# Load your original CSV
df = pd.read_csv("cleaned_data.csv")  # update the path if needed

# List of essential columns
essential_cols = [
    "Model Year",
    "Mfr Name",
    "Carline",
    "City FE (Guide) - Conventional Fuel",
    "Hwy FE (Guide) - Conventional Fuel",
    "Comb FE (Guide) - Conventional Fuel",
    "City CO2 Rounded Adjusted",
    "Hwy CO2 Rounded Adjusted",
    "Comb CO2 Rounded Adjusted (as shown on FE Label)"
]

# Keep only the essential columns
df_clean = df[essential_cols]

# Optionally, rename MPG columns for simplicity
df_clean = df_clean.rename(columns={
    "City FE (Guide) - Conventional Fuel": "City MPG",
    "Hwy FE (Guide) - Conventional Fuel": "Hwy MPG",
    "Comb FE (Guide) - Conventional Fuel": "Comb MPG"
})

# Save the cleaned CSV
df_clean.to_csv("data/essential_data.csv", index=False)

print("✅ Cleaned CSV saved as 'essential_data.csv'")
print(df_clean.head())
