import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ecocart.utils.api_client import APIClient
from src.ecocart.config import Config

class TestAPIClient(unittest.TestCase):
    
    def setUp(self):
        self.config = Config(
            BACKEND_URL="http://localhost:8000",
            MAX_RETRY_ATTEMPTS=2,
            RETRY_DELAY=0.1
        )
        self.api_client = APIClient(self.config)
        
    @patch('requests.Session.post')
    def test_add_item_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api_client.add_item("cart_001", "SKU00101", "apple", 0.8)
        self.assertTrue(result)
        mock_post.assert_called_once()
        
    @patch('requests.Session.post')
    def test_add_item_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = self.api_client.add_item("cart_001", "SKU00101", "apple", 0.8)
        self.assertFalse(result)
        
    @patch('requests.Session.get')
    def test_ping_backend(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.api_client.ping_backend()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()