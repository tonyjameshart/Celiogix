import sqlite3
db = sqlite3.connect("path/to/your/db.sqlite3")
db.execute("ALTER TABLE pantry ADD COLUMN upc TEXT;")
db.commit()
db.close()