# path: tests/test_db_perf.py  (edge index sanity)
from utils.db import get_connection
from utils.migrations import ensure_schema


def test_indexes_exist():
    conn = get_connection()
    ensure_schema(conn)
    idx = {row[1] for row in conn.execute("PRAGMA index_list('recipes')")}
    assert "idx_recipes_title" in idx
