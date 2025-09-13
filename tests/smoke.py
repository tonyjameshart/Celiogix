# path: tests/smoke.py
## Quick test to ensure the project imports
from utils.db import get_connection
from utils.migrations import ensure_schema

if __name__ == "__main__":
    conn = get_connection()
    ensure_schema(conn)
    print("DB ready, tables created.")
