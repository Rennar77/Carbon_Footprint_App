import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data/26clean_data.csv")
FINAL_PATH = os.path.join(BASE_DIR, "data/fuel_economy_final.csv")

df = pd.read_csv(CSV_PATH)

# Ensure only relevant columns
df = df[['make', 'model', 'year', 'fuel_type', 'co2_per_km']]

df.to_csv(FINAL_PATH, index=False)
print(f"✅ Prepared CSV saved: {FINAL_PATH}")
print(f"🧾 Total rows: {len(df)}")
