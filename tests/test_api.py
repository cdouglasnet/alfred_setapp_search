# tests/test_api.py
import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add src directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/script')))

import api

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Create test directory structure
        os.makedirs('cache', exist_ok=True)

        # Load test fixtures
        with open(os.path.join(os.path.dirname(__file__), 'fixtures/sample_apps.json'), 'r') as f:
            self.sample_apps = json.load(f)

    def tearDown(self):
        # Clean up test cache files
        if os.path.exists(api.CACHE_FILE):
            os.remove(api.CACHE_FILE)

    @patch('api.fetch_apps_from_api')
    def test_get_apps_data_from_api(self, mock_fetch):
        # Test successful API fetch
        mock_fetch.return_value = self.sample_apps
        result = api.get_apps_data()
        self.assertEqual(result, self.sample_apps)
        self.assertTrue(os.path.exists(api.CACHE_FILE))

    @patch('api.fetch_apps_from_api')
    def test_get_apps_data_from_cache(self, mock_fetch):
        # Test fallback to cache
        mock_fetch.side_effect = Exception("API unavailable")

        # Create a valid cache file
        os.makedirs(os.path.dirname(api.CACHE_FILE), exist_ok=True)
        with open(api.CACHE_FILE, 'w') as f:
            json.dump({
                'timestamp': api.time.time(),  # Current time
                'data': self.sample_apps
            }, f)

        result = api.get_apps_data()
        self.assertEqual(result, self.sample_apps)

    @patch('api.fetch_apps_from_api')
    def test_get_apps_data_from_fallback(self, mock_fetch):
        # Test fallback to embedded data when API fails and no cache exists
        mock_fetch.side_effect = Exception("API unavailable")

        # Ensure no cache file exists
        if os.path.exists(api.CACHE_FILE):
            os.remove(api.CACHE_FILE)

        # This should fall back to the embedded fallback data
        result = api.get_apps_data()

        # Should have called the API fetch function
        mock_fetch.assert_called_once()
        # Should return some data (fallback data) - API returns dict with 'items' key
        self.assertIsInstance(result, dict)
        self.assertIn('items', result)
        self.assertGreater(len(result['items']), 0)

if __name__ == '__main__':
    unittest.main()