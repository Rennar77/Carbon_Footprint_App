# recommendation_routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from services.ai_services import generate_recommendation
from services.badge_service import award_badges_for_user
from services.log_service import get_user_summary  # async function

from core.database import get_db

router = APIRouter(prefix="/api")


@router.get("/recommendation/{user_id}")
async def get_recommendation(user_id: int) -> Dict[str, Any]:
    """
    Returns an AI recommendation plus any newly earned badges (with details).
    """
    # ✅ await async user summary
    summary = await get_user_summary(user_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="User summary not found")

    # 1️⃣ Generate AI recommendation based on user summary
    recommendation = await generate_recommendation(summary)

    # 2️⃣ Award badges and get newly earned badge codes
    new_badge_codes = await award_badges_for_user(user_id)

    # 3️⃣ Fetch badge details for the new badges
    badges: List[Dict[str, str]] = []
    if new_badge_codes:
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT code, name, description FROM badges WHERE code = ANY(%s)",
                (new_badge_codes,)  # ✅ ensure this is a list/tuple
            )
            for row in cur.fetchall():
                badges.append({
                    "code": row[0],
                    "name": row[1],
                    "description": row[2]
                })
            cur.close()
        finally:
            conn.close()

    return {
        "recommendation": recommendation,
        "badges": badges
    }
