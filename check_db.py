import sqlite3
import os

db_path = r"c:\Users\india\Desktop\fswd\db.sqlite3"
print(f"File exists: {os.path.exists(db_path)}")
print(f"File size: {os.path.getsize(db_path)} bytes")

c = sqlite3.connect(db_path)
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables in database:")
for t in tables:
    print(f"- {t[0]}")
    
# check records in medicalentry
try:
    records = c.execute("SELECT * FROM tactical_ui_medicalentry").fetchall()
    print(f"Records in tactical_ui_medicalentry: {len(records)}")
except Exception as e:
    print(f"Error querying table: {e}")
