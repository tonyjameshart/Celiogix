# path: tests/test_pantry_crud.py
import unittest

from utils.db import get_connection
from utils.migrations import ensure_schema


class PantryCRUDTest(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection()
        ensure_schema(self.conn)
        self.c = self.conn.cursor()

    def test_insert_update_delete(self):
        self.c.execute(
            "INSERT INTO pantry(name,brand,subcategory,net_weight,unit,thresh,notes,category) VALUES(?,?,?,?,?,?,?,?)",
            ("Test Item", "BrandX", "Snacks", 1.0, "kg", 0.0, "note", "Snacks"),
        )
        pid = self.c.lastrowid
        self.conn.commit()

        row = self.c.execute("SELECT name,unit FROM pantry WHERE id=?", (pid,)).fetchone()
        self.assertEqual(row["name"], "Test Item")
        self.assertEqual(row["unit"], "kg")

        self.c.execute("UPDATE pantry SET unit=? WHERE id=?", ("g", pid))
        self.conn.commit()
        row = self.c.execute("SELECT unit FROM pantry WHERE id=?", (pid,)).fetchone()
        self.assertEqual(row["unit"], "g")

        self.c.execute("DELETE FROM pantry WHERE id=?", (pid,))
        self.conn.commit()
        gone = self.c.execute("SELECT id FROM pantry WHERE id=?", (pid,)).fetchone()
        self.assertIsNone(gone)


if __name__ == "__main__":
    unittest.main()
