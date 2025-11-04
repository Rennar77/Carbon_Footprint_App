from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from CORE.database import get_db
from services.badge_service import award_badges_for_user
from datetime import datetime
import psycopg2.extras

router = APIRouter()

# ---------- Models ----------
class CarLog(BaseModel):
    vehicle_name: str
    distance: float
    category: str | None = None

class ElectricityLog(BaseModel):
    kwh: float
    region: str

class FlightLog(BaseModel):
    distance_km: float
    class_type: str

class CookingLog(BaseModel):
    type: str
    kg_used: float


# ---------- Helpers ----------
def save_activity(conn, user_id, activity_type, activity_data, co2_kg):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO activities (user_id, activity_type, activity_data, co2_kg, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, activity_type, activity_data, co2_kg, datetime.utcnow())
        )
        conn.commit()


# ---------- Routes ----------

@router.post("/car")
def log_car(data: CarLog, user_id: int = 1):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    make_model = data.vehicle_name.strip().lower()
    cur.execute("SELECT * FROM vehicles WHERE LOWER(make || ' ' || model) = %s LIMIT 1", (make_model,))
    vehicle = cur.fetchone()

    if vehicle:
        co2_per_km = vehicle["comb_co2"] / vehicle["comb_mpg"]
        co2_kg = (data.distance * co2_per_km) / 1000
    else:
        # fallback estimate if vehicle not found
        co2_kg = data.distance * 0.12

    save_activity(conn, user_id, "car", {"vehicle": data.vehicle_name, "distance": data.distance}, co2_kg)
    award_badges_for_user(user_id, "car")
    return {"co2_kg": co2_kg}


@router.post("/electricity")
def log_electricity(data: ElectricityLog, user_id: int = 1):
    region_factors = {"KE": 0.43, "US": 0.41, "EU": 0.29, "NG": 0.52, "ZA": 0.94, "IN": 0.75, "CN": 0.64}
    factor = region_factors.get(data.region.upper(), 0.5)
    co2_kg = data.kwh * factor
    conn = get_db()
    save_activity(conn, user_id, "electricity", {"kwh": data.kwh, "region": data.region}, co2_kg)
    award_badges_for_user(user_id, "electricity")
    return {"co2_kg": co2_kg}


@router.post("/flight")
def log_flight(data: FlightLog, user_id: int = 1):
    class_factors = {"economy": 0.09, "business": 0.15, "first": 0.25}
    factor = class_factors.get(data.class_type.lower(), 0.09)
    co2_kg = data.distance_km * factor
    conn = get_db()
    save_activity(conn, user_id, "flight", {"distance_km": data.distance_km, "class": data.class_type}, co2_kg)
    award_badges_for_user(user_id, "flight")
    return {"co2_kg": co2_kg}


@router.post("/cooking")
def log_cooking(data: CookingLog, user_id: int = 1):
    cooking_factors = {"charcoal": 2.83, "lpg": 3.0, "electric": 0.5, "firewood": 1.6}
    factor = cooking_factors.get(data.type.lower(), 1.0)
    co2_kg = data.kg_used * factor
    conn = get_db()
    save_activity(conn, user_id, "cooking", {"type": data.type, "kg_used": data.kg_used}, co2_kg)
    award_badges_for_user(user_id, "cooking")
    return {"co2_kg": co2_kg}
