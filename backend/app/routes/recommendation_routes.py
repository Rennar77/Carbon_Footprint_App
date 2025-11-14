# recommendation_routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from services.ai_services import generate_recommendation
from services.badge_service import award_badges_for_user
from services.log_service import get_user_summary
from core.database import get_db
import re

router = APIRouter(prefix="/api")


def strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> blocks from AI output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


@router.get("/recommendation/{user_id}")
async def get_recommendation(user_id: int) -> Dict[str, Any]:

    # --- 1) Get user summary ---
    summary = await get_user_summary(user_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="User summary not found")

    # --- 2) Get AI recommendation ---
    ai_output = await generate_recommendation(summary)

    # Clean DeepSeek reasoning
    recommendation = strip_think_blocks(ai_output)

    # --- 3) Award badges ---
    new_badge_codes = await award_badges_for_user(user_id)

    # --- 4) ALWAYS return all user badges ---
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.code, b.name, b.description
        FROM badges b
        JOIN user_badges ub ON ub.badge_id = b.id
        WHERE ub.user_id = %s
    """, (user_id,))

    all_badges = cur.fetchall()
    cur.close()
    conn.close()

    # Build badge list with a `new` flag
    badges = []
    for code, name, desc in all_badges:
        badges.append({
            "code": code,
            "name": name,
            "description": desc,
            "new": code in new_badge_codes
        })

    return {
        "recommendation": recommendation,
        "badges": badges
    }
