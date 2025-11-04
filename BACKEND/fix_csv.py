import pandas as pd

# Input CSV
input_csv = r"C:/Users/renar/Desktop/plp/Carbon_Footprint_App/BACKEND/data/essential_data.csv"

# Output CSV (PostgreSQL-ready)
output_csv = r"C:/Users/renar/Desktop/plp/Carbon_Footprint_App/BACKEND/data/essential_pg.csv"

# Load the CSV
df = pd.read_csv(input_csv)

# Rename columns to match your PostgreSQL table
df = df.rename(columns={
    "Mfr Name": "make",
    "Carline": "model",
    "Model Year": "year",
    "City MPG": "city_mpg",
    "Hwy MPG": "hwy_mpg",
    "Comb MPG": "comb_mpg",
    "City CO2 Rounded Adjusted": "city_co2",
    "Hwy CO2 Rounded Adjusted": "hwy_co2",
    "Comb CO2 Rounded Adjusted (as shown on FE Label)": "comb_co2"
})

# Reorder columns exactly as PostgreSQL table expects
df = df[["make","model","year","city_mpg","hwy_mpg","comb_mpg","city_co2","hwy_co2","comb_co2"]]

# Save CSV without quotes
df.to_csv(output_csv, index=False)
print("PostgreSQL-ready CSV saved at:", output_csv)