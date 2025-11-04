import sqlite3

DB = "db/carbon.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT id, mfr_name, carline, year FROM vehicles")
rows = cur.fetchall()

for r in rows:
    print(r)

conn.close()
