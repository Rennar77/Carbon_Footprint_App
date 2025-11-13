# log_service.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.database import get_db
from services.badge_service import award_badges_for_user
from services.auth_service import get_current_user
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2.extras
import json
import asyncio

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
    """Safely insert user activity into DB as JSON."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO activities (user_id, activity_type, activity_data, co2_kg, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    activity_type,
                    json.dumps(activity_data),
                    co2_kg,
                    datetime.utcnow()
                )
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---------- Routes ----------
@router.post("/car")
async def log_car(data: CarLog, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        make_model = data.vehicle_name.strip().lower()
        cur.execute(
            "SELECT * FROM vehicles WHERE LOWER(make || ' ' || model) = %s LIMIT 1",
            (make_model,)
        )
        vehicle = cur.fetchone()

        if vehicle and vehicle.get("comb_mpg") and vehicle.get("comb_co2"):
            co2_per_km = vehicle["comb_co2"] / vehicle["comb_mpg"] if vehicle["comb_mpg"] != 0 else 0.12
            co2_kg = (data.distance * co2_per_km) / 1000
        else:
            co2_kg = data.distance * 0.12  # fallback estimate

        save_activity(conn, user_id, "car", {"vehicle": data.vehicle_name, "distance": data.distance}, co2_kg)

        # ✅ await async badge awarding
        await award_badges_for_user(user_id)

        return {"co2_kg": round(co2_kg, 3)}

    finally:
        conn.close()


@router.post("/electricity")
async def log_electricity(data: ElectricityLog, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    region_factors = {"KE": 0.43, "US": 0.41, "EU": 0.29, "NG": 0.52, "ZA": 0.94, "IN": 0.75, "CN": 0.64}
    factor = region_factors.get(data.region.upper(), 0.5)
    co2_kg = data.kwh * factor

    conn = get_db()
    try:
        save_activity(conn, user_id, "electricity", {"kwh": data.kwh, "region": data.region}, co2_kg)
        await award_badges_for_user(user_id)
        return {"co2_kg": round(co2_kg, 3)}
    finally:
        conn.close()


@router.post("/flight")
async def log_flight(data: FlightLog, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    class_factors = {"economy": 0.09, "business": 0.15, "first": 0.25}
    factor = class_factors.get(data.class_type.lower(), 0.09)
    co2_kg = data.distance_km * factor

    conn = get_db()
    try:
        save_activity(conn, user_id, "flight", {"distance_km": data.distance_km, "class": data.class_type}, co2_kg)
        await award_badges_for_user(user_id)
        return {"co2_kg": round(co2_kg, 3)}
    finally:
        conn.close()


@router.post("/cooking")
async def log_cooking(data: CookingLog, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    cooking_factors = {"charcoal": 2.83, "lpg": 3.0, "electric": 0.5, "firewood": 1.6}
    factor = cooking_factors.get(data.type.lower(), 1.0)
    co2_kg = data.kg_used * factor

    conn = get_db()
    try:
        save_activity(conn, user_id, "cooking", {"type": data.type, "kg_used": data.kg_used}, co2_kg)
        await award_badges_for_user(user_id)
        return {"co2_kg": round(co2_kg, 3)}
    finally:
        conn.close()


# ---------- User summary ----------
async def get_user_summary(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Returns a summary of user's logged activities.
    Example:
    {
        "total_co2": 123.4,
        "by_category": {
            "car": 45.6,
            "cooking": 20.0,
            "flight": 57.8
        },
        "activities_count": {
            "car": 5,
            "cooking": 2,
            "flight": 1
        }
    }
    """
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT SUM(co2_kg) as total_co2 FROM activities WHERE user_id=%s",
            (user_id,)
        )
        total_row = cur.fetchone()
        total_co2 = total_row["total_co2"] or 0.0

        cur.execute(
            "SELECT activity_type, SUM(co2_kg) as co2, COUNT(*) as count "
            "FROM activities WHERE user_id=%s GROUP BY activity_type",
            (user_id,)
        )
        rows = cur.fetchall()
        by_category = {}
        activities_count = {}
        for r in rows:
            by_category[r["activity_type"]] = float(r["co2"] or 0)
            activities_count[r["activity_type"]] = r["count"]

        return {
            "total_co2": float(total_co2),
            "by_category": by_category,
            "activities_count": activities_count
        }
    except Exception:
        return None
    finally:
        conn.close()
