import sqlite3

conn = sqlite3.connect("db/carbon.db")
cur = conn.cursor()

cur.execute("SELECT make, model, year, city_mpg, hwy_mpg, comb_mpg, city_co2, hwy_co2, comb_co2 FROM vehicles LIMIT 5")
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()
