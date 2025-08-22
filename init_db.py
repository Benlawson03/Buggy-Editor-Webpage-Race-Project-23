import sqlite3

DATABASE_FILE = "database.db"

connection = sqlite3.connect(DATABASE_FILE)
print(f"- Opened database successfully in file \"{DATABASE_FILE}\"")

connection.execute("""

  CREATE TABLE IF NOT EXISTS buggies (
    id                    INTEGER PRIMARY KEY,
    qty_wheels            INTEGER DEFAULT 4,
    flag_color            VARCHAR(20),
    flag_color_secondary  VARCHAR(20),
    flag_pattern          VARCHAR(20),
    algo                  VARCHAR(20),
    total_cost            INTEGER DEFAULT 250              
  )

""")

print("- OK, table \"buggies\" exists")

cursor = connection.cursor()

cursor.execute("SELECT * FROM buggies LIMIT 1")
rows = cursor.fetchall()
if len(rows) == 0:
    cursor.execute("INSERT INTO buggies (qty_wheels) VALUES (4)")
    connection.commit()
    print("- Added one 4-wheeled buggy")
else:
    print("- Found a buggy in the database, nice")

print("- OK, your database is ready")

connection.close()
