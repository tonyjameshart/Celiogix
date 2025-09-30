# path: tests/test_schema.py
import unittest

from utils.db import get_connection
from utils.migrations import ensure_schema


class SchemaTest(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection()
        ensure_schema(self.conn)

    def test_pantry_columns(self):
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(pantry)")}
        expected = {
            "id",
            "name",
            "brand",
            "category",
            "subcategory",
            "net_weight",
            "unit",
            "quantity",
            "store",
            "expiration",
            "gf_flag",
            "tags",
            "notes",
        }
        self.assertTrue(expected.issubset(cols), f"Missing columns: {expected - cols}")

    def test_shopping_columns(self):
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(shopping_list)")}
        expected = {
            "id",
            "name",
            "brand",
            "category",
            "net_weight",
            "thresh",
            "store",
            "notes",
            "created_at",
        }
        self.assertTrue(expected.issubset(cols), f"Missing columns: {expected - cols}")


if __name__ == "__main__":
    unittest.main()
