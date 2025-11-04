import sqlite3

conn = sqlite3.connect("db/carbon.db")
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS vehicles")
conn.commit()
conn.close()
