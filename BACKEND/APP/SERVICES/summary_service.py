from fastapi import APIRouter, Depends, HTTPException
import psycopg2.extras
from app.core.database import get_db
from app.services.auth_service import get_current_user

router = APIRouter()  # no prefix here

def get_dashboard_summary(user_id: int):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cur.execute("""
            SELECT activity_type, COALESCE(SUM(co2_kg),0) AS total_co2
            FROM activities
            WHERE user_id = %s
            GROUP BY activity_type
        """, (user_id,))
        rows = cur.fetchall()
        summary = {row["activity_type"]: round(row["total_co2"], 3) for row in rows}
        total = round(sum(summary.values()), 3)
        return {"summary": summary, "total_co2": total}

    finally:
        cur.close()
        conn.close()

@router.get("/summary")
def dashboard_summary(current_user: dict = Depends(get_current_user)):
    try:
        return get_dashboard_summary(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
