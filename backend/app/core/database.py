import psycopg2
from app.core.config import DB_PARAMS

def get_db():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    return conn
