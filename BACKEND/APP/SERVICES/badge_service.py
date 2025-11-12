import psycopg2.extras
from core.database import get_db

def award_badges_for_user(user_id: int):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

    cur.close()
    conn.close()
