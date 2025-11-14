from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import get_current_user
from app.core.database import get_db
from app.schemas.trip_schema import CarLog, ElectricityLog, FlightLog
from app.schemas.cooking_schema import CookingLog
import psycopg2.extras, json

router = APIRouter(tags=["Logs"])

# Regional electricity CO₂ factors (kg CO₂ per kWh)
REGION_FACTORS = {
    "KE": 0.72,  # Kenya
    "US": 0.4,   # United States
    "EU": 0.25,  # Europe
    "NG": 0.65,  # Nigeria
    "ZA": 0.58,  # South Africa
    "IN": 0.7,   # India
    "CN": 0.76,  # China
}


# ---------------- ELECTRICITY ----------------
@router.post("/log/electricity")
def log_electricity(data: ElectricityLog, user: dict = Depends(get_current_user)):
    factor = REGION_FACTORS.get(data.region.upper(), 0.5)
    co2_kg = data.kwh * factor

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO activities (user_id, activity_type, activity_data, co2_kg) VALUES (%s, %s, %s, %s)",
        (user["id"], "electricity", json.dumps(data.dict()), co2_kg),
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"co2_kg": round(co2_kg, 3)}


# ---------------- COOKING ----------------
@router.post("/log/cooking")
def log_cooking(data: CookingLog, user: dict = Depends(get_current_user)):
    factors = {"charcoal": 2.7, "lpg": 1.5}  # Base kg CO₂ per kg of fuel used

    if data.type.lower() not in factors:
        raise HTTPException(status_code=400, detail="Invalid cooking type")

    co2_kg = factors[data.type.lower()] * data.kg_used

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO activities (user_id, activity_type, activity_data, co2_kg) VALUES (%s, %s, %s, %s)",
        (user["id"], "cooking", json.dumps(data.dict()), co2_kg),
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"co2_kg": round(co2_kg, 3)}


# ---------------- CAR ----------------
@router.post("/log/car")
def log_car_trip(payload: dict, user: dict = Depends(get_current_user)):
    """
    Expected payload:
    {
      "vehicle": "BMW Z4 M40i" OR "My Toyota Probox",
      "distance_km": 120,
      "category": "sedan" | "suv" | "midsize_suv" (optional)
    }
    """
    vehicle_name = payload.get("vehicle")
    distance_km = payload.get("distance_km")
    category = payload.get("category")  # optional hint from frontend

    if not vehicle_name or not distance_km:
        raise HTTPException(status_code=400, detail="Missing vehicle or distance")

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 1️⃣ Try to find exact match in DB
    cur.execute("""
        SELECT make, model, comb_co2
        FROM vehicle
        WHERE CONCAT(make, ' ', model) ILIKE %s
        LIMIT 1
    """, (f"%{vehicle_name}%",))
    vehicle = cur.fetchone()

    # 2️⃣ Define fallback emission factors (grams CO₂ per km)
    fallback_factors = {
        "sedan": 180,
        "midsize_suv": 230,
        "suv": 260,
    }

    # 3️⃣ If no DB match → estimate by category
    if not vehicle:
        # Guess based on keywords if category not given
        lower_name = vehicle_name.lower()
        if not category:
            if any(x in lower_name for x in ["suv", "crv", "rav4", "xtrail", "sportage", "outlander", "santa fe", "fortuner", "land cruiser"]):
                category = "suv"
            elif any(x in lower_name for x in ["van", "noah", "stepwagon", "hiace", "odyssey"]):
                category = "midsize_suv"
            else:
                category = "sedan"  # default

        factor = fallback_factors.get(category, 200)
        co2_kg = (factor * distance_km) / 1000.0
        vehicle_info = {"vehicle": vehicle_name, "category": category, "comb_co2": factor}
    else:
        co2_kg = (vehicle["comb_co2"] * distance_km) / 1000.0
        vehicle_info = {"vehicle": f"{vehicle['make']} {vehicle['model']}", "comb_co2": vehicle["comb_co2"]}

    # 4️⃣ Log the result in DB
    cur.execute("""
        INSERT INTO activities (user_id, activity_type, activity_data, co2_kg)
        VALUES (%s, %s, %s, %s)
    """, (
        user["id"],
        "car_trip",
        json.dumps({
            "vehicle": vehicle_info["vehicle"],
            "distance_km": distance_km,
            "comb_co2": vehicle_info["comb_co2"],
            "category": category or "exact match"
        }),
        co2_kg,
    ))
    conn.commit()

    cur.close()
    conn.close()

    return {
        "vehicle": vehicle_info["vehicle"],
        "category": category or "exact match",
        "distance_km": distance_km,
        "co2_kg": round(co2_kg, 3)
    }

# ---------------- FLIGHT ----------------
@router.post("/log/flight")
def log_flight(data: FlightLog, user: dict = Depends(get_current_user)):
    """
    Basic flight emission model:
    - Economy: 0.09 kg/km
    - Business: 0.18 kg/km
    """
    if data.class_type.lower() not in ["economy", "business"]:
        raise HTTPException(status_code=400, detail="Invalid flight class type")

    factor = 0.09 if data.class_type.lower() == "economy" else 0.18
    co2_kg = data.distance_km * factor

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO activities (user_id, activity_type, activity_data, co2_kg) VALUES (%s, %s, %s, %s)",
        (user["id"], "flight", json.dumps(data.dict()), co2_kg),
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"co2_kg": round(co2_kg, 3)}
