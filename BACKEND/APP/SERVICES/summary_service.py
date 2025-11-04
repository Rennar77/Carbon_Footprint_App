from fastapi import APIRouter, Depends, HTTPException
import psycopg2.extras
from CORE.database import get_db
from services.auth_service import get_current_user

# -----------------------------
# Router setup
# -----------------------------
router = APIRouter()

# -----------------------------
# Dashboard summary logic
# -----------------------------
def get_dashboard_summary(user_id: int):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT activity_type, SUM(co2_kg) AS total_co2
        FROM activities
        WHERE user_id = %s
        GROUP BY activity_type
    """, (user_id,))
    rows = cur.fetchall()

    summary = {row["activity_type"]: round(row["total_co2"], 3) for row in rows}
    total = sum(summary.values())

    cur.close()
    conn.close()

    return {"summary": summary, "total_co2": round(total, 3)}

# -----------------------------
# API route
# -----------------------------
@router.get("/")
def dashboard_summary(current_user: dict = Depends(get_current_user)):
    """
    Returns CO₂ summary and totals for the logged-in user.
    """
    try:
        return get_dashboard_summary(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
