#!/usr/bin/env python3
"""
Unit tests for database operations
"""

import unittest
import sys
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_connection, execute_with_retry, safe_commit


class TestDatabase(unittest.TestCase):
    """Test cases for database operations"""
    
    def setUp(self):
        """Set up each test with temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Mock the database path
        with patch('utils.db._db_path') as mock_path:
            mock_path.return_value = self.temp_db.name
            self.conn = get_connection()
    
    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()
        os.unlink(self.temp_db.name)
    
    def test_database_connection(self):
        """Test database connection works"""
        self.assertIsInstance(self.conn, sqlite3.Connection)
        self.assertFalse(self.conn.closed)
    
    def test_database_foreign_keys_enabled(self):
        """Test foreign keys are enabled"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()[0]
        self.assertEqual(result, 1)
    
    def test_database_journal_mode(self):
        """Test journal mode is WAL"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        result = cursor.fetchone()[0]
        self.assertEqual(result.upper(), 'WAL')
    
    def test_create_table(self):
        """Test table creation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        safe_commit(self.conn)
        
        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
    
    def test_execute_with_retry_success(self):
        """Test execute_with_retry on successful operation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Should not raise exception
        execute_with_retry(self.conn, "INSERT INTO test_table (name) VALUES (?)", ("test",))
        safe_commit(self.conn)
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
    
    def test_safe_commit(self):
        """Test safe commit functionality"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        
        # Should not raise exception
        safe_commit(self.conn)
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
