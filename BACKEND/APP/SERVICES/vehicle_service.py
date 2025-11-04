from fastapi import APIRouter, HTTPException
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def get_db():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    return conn


@router.get("/")
def get_vehicles():
    """Fetch all vehicles from the database"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cur.execute("SELECT id, make, model, year, fuel_type FROM vehicle")
        rows = cur.fetchall()

        vehicles = [
            {
                "id": row["id"],
                "make": row["make"],
                "model": row["model"],
                "year": row["year"],
                "fuel_type": row["fuel_type"],
            }
            for row in rows
        ]

        return {"vehicles": vehicles}

    except Exception as e:
        print("Error fetching vehicles:", e)
        raise HTTPException(status_code=500, detail="Error fetching vehicles")
    finally:
        cur.close()
        conn.close()
