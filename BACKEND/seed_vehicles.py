# seed_vehicles.py
import csv
import sqlite3
from decimal import Decimal, getcontext

getcontext().prec = 9

GRAMS_CO2_PER_LITER_PETROL = Decimal("2392")
GRAMS_CO2_PER_LITER_DIESEL = Decimal("2640")
MILES_TO_KM = Decimal("1.609344")
LITERS_PER_GALLON_US = Decimal("3.785411784")

def mpg_to_grams_per_km(mpg, fuel_type_hint="petrol"):
    mpg = Decimal(str(mpg))
    liters_per_km = LITERS_PER_GALLON_US / (mpg * MILES_TO_KM)
    gpl = GRAMS_CO2_PER_LITER_PETROL if fuel_type_hint.lower().startswith("pet") else GRAMS_CO2_PER_LITER_DIESEL
    return float(liters_per_km * gpl)

def seed(csv_path, db_path="db/carbon.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # strip column names to remove any whitespace
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        rows = list(reader)

    inserted = 0
    for r in rows:
        try:
            make = r.get("Mfr Name") or ""
            model = r.get("Carline") or ""
            year = int(r.get("Model Year") or 0)

            city_mpg = float(r["City MPG"]) if r.get("City MPG") else None
            hwy_mpg  = float(r["Hwy MPG"]) if r.get("Hwy MPG") else None
            comb_mpg = float(r["Comb MPG"]) if r.get("Comb MPG") else None

            city_co2 = float(r["City CO2 Rounded Adjusted"]) if r.get("City CO2 Rounded Adjusted") else None
            hwy_co2  = float(r["Hwy CO2 Rounded Adjusted"]) if r.get("Hwy CO2 Rounded Adjusted") else None
            comb_co2 = float(r["Comb CO2 Rounded Adjusted (as shown on FE Label)"]) if r.get("Comb CO2 Rounded Adjusted (as shown on FE Label)") else None

            # fallback grams_per_km
            grams_per_km = comb_co2 if comb_co2 else (mpg_to_grams_per_km(comb_mpg) if comb_mpg else None)
            if grams_per_km is None:
                continue

            cur.execute("""
                INSERT INTO vehicles (make, model, year, city_mpg, hwy_mpg, comb_mpg, city_co2, hwy_co2, comb_co2, grams_per_km)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (make, model, year, city_mpg, hwy_mpg, comb_mpg, city_co2, hwy_co2, comb_co2, grams_per_km))

            inserted += 1
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"Seeded {inserted} vehicles into {db_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed vehicles table from CSV.")
    parser.add_argument("csv", help="data/essentia_data.csv")
    parser.add_argument("--db", default="db/carbon.db", help="sqlite db path")
    args = parser.parse_args()
    seed(args.csv, args.db)
