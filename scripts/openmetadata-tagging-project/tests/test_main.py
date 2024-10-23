import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.main import check_table_exists, apply_tag, process_table_batch

class TestMainFunctions(unittest.TestCase):

    @patch('src.main.requests.get')
    def test_check_table_exists(self, mock_get):
        # Test when table exists
        mock_get.return_value.status_code = 200
        self.assertTrue(check_table_exists('base_url', {}, 'table_fqn'))

        # Test when table doesn't exist
        mock_get.return_value.status_code = 404
        self.assertFalse(check_table_exists('base_url', {}, 'table_fqn'))

    @patch('src.main.requests.patch')
    @patch('src.main.requests.get')
    def test_apply_tag(self, mock_get, mock_patch):
        # Mock the GET request to return a table without the tag
        mock_get.return_value.json.return_value = {'tags': []}
        mock_get.return_value.status_code = 200
        
        # Mock the PATCH request to succeed
        mock_patch.return_value.status_code = 200

        result = apply_tag('base_url', {}, 'table_fqn', 'tag_fqn')
        self.assertTrue(result)

    @patch('src.main.check_table_exists')
    @patch('src.main.apply_tag')
    def test_process_table_batch(self, mock_apply_tag, mock_check_table_exists):
        mock_check_table_exists.return_value = True
        mock_apply_tag.return_value = True

        tables = [('table1', {'fqn': 'fqn1'}), ('table2', {'fqn': 'fqn2'})]
        result = process_table_batch('base_url', {}, tables, 'tag_fqn', True)

        self.assertEqual(result, (2, 0, 2, 0))  # 2 existing tables, 0 missing, 2 tags applied, 0 failed

if __name__ == '__main__':
    unittest.main()