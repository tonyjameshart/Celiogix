#!/usr/bin/env python3
"""
Unit tests for utility functions
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import fetch_all, delete_with_dependents


class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_fetch_all_success(self):
        """Test fetch_all with successful query"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [('test1',), ('test2',)]
        mock_db.execute.return_value = mock_cursor
        
        result = fetch_all(mock_db, "SELECT * FROM test_table")
        
        self.assertEqual(result, [('test1',), ('test2',)])
        mock_db.execute.assert_called_once_with("SELECT * FROM test_table", ())
    
    def test_fetch_all_with_params(self):
        """Test fetch_all with parameters"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [('test1',)]
        mock_db.execute.return_value = mock_cursor
        
        result = fetch_all(mock_db, "SELECT * FROM test_table WHERE id = ?", (1,))
        
        self.assertEqual(result, [('test1',)])
        mock_db.execute.assert_called_once_with("SELECT * FROM test_table WHERE id = ?", (1,))
    
    def test_fetch_all_exception(self):
        """Test fetch_all with database exception"""
        mock_db = Mock()
        mock_db.execute.side_effect = Exception("Database error")
        
        with patch('builtins.print') as mock_print:
            result = fetch_all(mock_db, "SELECT * FROM test_table")
            
            self.assertEqual(result, [])
            mock_print.assert_called_once()
    
    def test_delete_with_dependents(self):
        """Test delete_with_dependents function"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (5,)  # 5 rows affected
        mock_conn.execute.return_value = mock_cursor
        
        result = delete_with_dependents(mock_conn, 'parent_table', 'parent_id', [1, 2, 3])
        
        self.assertEqual(result, 5)
        mock_conn.execute.assert_called()


if __name__ == '__main__':
    unittest.main()
