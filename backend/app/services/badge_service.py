# services/badge_service.py
import psycopg2.extras
from core.database import get_db

async def award_badges_for_user(user_id: int):
    from services.log_service import get_user_summary  # lazy import to avoid circular import

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    newly_earned = []

    # Starter badge logic
    cur.execute("SELECT COUNT(*) as c FROM activities WHERE user_id=%s", (user_id,))
    count = cur.fetchone()["c"]

    cur.execute("SELECT id FROM badges WHERE code='starter'")
    row = cur.fetchone()
    if row is None:
        cur.execute(
            "INSERT INTO badges (code,name,description,threshold) VALUES (%s,%s,%s,%s) RETURNING id",
            ("starter", "Getting Started", "Logged your first activity", 1)
        )
        badge_id = cur.fetchone()["id"]
    else:
        badge_id = row["id"]

    cur.execute("SELECT 1 FROM user_badges WHERE user_id=%s AND badge_id=%s", (user_id, badge_id))
    if count >= 1 and cur.fetchone() is None:
        cur.execute("INSERT INTO user_badges (user_id,badge_id) VALUES (%s,%s)", (user_id, badge_id))
        newly_earned.append("starter")

    # Metric/AI-based badges
    summary = await get_user_summary(user_id)  # ✅ await
    if summary:
        total_emission = summary.get("total_emission", 0)
        vehicle_logs = summary.get("vehicle_logs", 0)
        cooking_emission = summary.get("cooking_emission", 0)

        badge_definitions = [
            {"code": "eco_beginner", "name": "Eco Beginner", "description": "Kept emissions below 50kg CO₂.", "threshold": 50, "condition": total_emission < 50},
            {"code": "frequent_traveler", "name": "Frequent Traveler", "description": "Logged over 10 trips.", "threshold": 10, "condition": vehicle_logs >= 10},
            {"code": "efficient_cook", "name": "Efficient Cook", "description": "Maintained low cooking emissions.", "threshold": 5, "condition": cooking_emission < 5},
        ]

        for badge in badge_definitions:
            if badge["condition"]:
                cur.execute("SELECT id FROM badges WHERE code=%s", (badge["code"],))
                row = cur.fetchone()
                if row is None:
                    cur.execute(
                        "INSERT INTO badges (code, name, description, threshold) VALUES (%s,%s,%s,%s) RETURNING id",
                        (badge["code"], badge["name"], badge["description"], badge["threshold"])
                    )
                    badge_id = cur.fetchone()["id"]
                else:
                    badge_id = row["id"]

                cur.execute("SELECT 1 FROM user_badges WHERE user_id=%s AND badge_id=%s", (user_id, badge_id))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO user_badges (user_id,badge_id) VALUES (%s,%s)", (user_id, badge_id))
                    newly_earned.append(badge["code"])

    conn.commit()
    cur.close()
    conn.close()
    return newly_earned
