import sqlite3

conn = sqlite3.connect("db/carbon.db")
with open("db/init.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()
conn.executescript(sql_script)
conn.close()

print("DB created and initialized!")
