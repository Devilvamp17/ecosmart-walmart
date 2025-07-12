import requests
import time
import logging
from typing import Dict, Any, Optional
from src.ecocart.config import Config

class APIClient:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[Any, Any]] = None, 
                     max_retries: Optional[int] = None) -> bool:
        """Make API request with retry logic"""
        if max_retries is None:
            max_retries = self.config.MAX_RETRY_ATTEMPTS
            
        url = f"{self.config.BACKEND_URL}/{endpoint}"
        
        for attempt in range(max_retries):
            try:
                if method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=self.config.API_TIMEOUT)
                elif method.upper() == "GET":
                    response = self.session.get(url, timeout=self.config.API_TIMEOUT)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
                if response.status_code == 200:
                    return True
                else:
                    self.logger.warning(f"API request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                self.logger.error(f"API request timeout (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"API connection error (attempt {attempt + 1}/{max_retries})")
            except Exception as e:
                self.logger.error(f"API request error (attempt {attempt + 1}/{max_retries}): {e}")
                
            if attempt < max_retries - 1:
                time.sleep(self.config.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                
        return False
        
    def add_item(self, cart_id: str, sku: str, label: str, confidence: float) -> bool:
        """Add item to cart"""
        data = {
            "cart_id": cart_id,
            "sku": sku,
            "label": label,
            "confidence": confidence,
            "timestamp": time.time()
        }
        return self._make_request("POST", "add_item", data)
        
    def remove_item(self, cart_id: str, sku: str, label: str) -> bool:
        """Remove item from cart"""
        data = {
            "cart_id": cart_id,
            "sku": sku,
            "label": label,
            "timestamp": time.time()
        }
        return self._make_request("POST", "remove_item", data)
        
    def get_cart_summary(self, cart_id: str) -> Optional[Dict[Any, Any]]:
        """Get cart summary"""
        try:
            response = self.session.get(
                f"{self.config.BACKEND_URL}/cart/{cart_id}/summary",
                timeout=self.config.API_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get cart summary: {e}")
        return None
        
    def ping_backend(self) -> bool:
        """Check if backend is alive"""
        try:
            response = self.session.get(
                f"{self.config.BACKEND_URL}/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
def send_test_request():
        from src.ecocart.config import Config
        client = APIClient(Config())
        is_alive = client.ping_backend()
        return {"status": "alive" if is_alive else "unreachable"}