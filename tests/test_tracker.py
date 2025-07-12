import unittest
import sys
import os
import tempfile
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ecocart.main import GroceryCartTracker, DetectedItem
from src.ecocart.config import Config

class TestGroceryCartTracker(unittest.TestCase):
    
    def setUp(self):
        # Create temporary SKU map file
        self.temp_sku_map = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        sku_map = {
            "apple": "SKU00101",
            "orange": "SKU00102"
        }
        json.dump(sku_map, self.temp_sku_map)
        self.temp_sku_map.close()
        
        # Create test configuration
        self.config = Config(
            CART_ID="test_cart",
            BACKEND_URL="http://localhost:8000",
            LABEL_MAP_PATH=self.temp_sku_map.name,
            MODEL_PATH="yolov8n.pt",
            DISPLAY_WINDOW=False
        )
        
    def tearDown(self):
        os.unlink(self.temp_sku_map.name)
        
    def test_iou_calculation(self):
        tracker = GroceryCartTracker(self.config)
        
        # Test perfect overlap
        box1 = (10, 10, 50, 50)
        box2 = (10, 10, 50, 50)
        iou = tracker.calculate_iou(box1, box2)
        self.assertEqual(iou, 1.0)
        
        # Test no overlap
        box1 = (10, 10, 50, 50)
        box2 = (60, 60, 100, 100)
        iou = tracker.calculate_iou(box1, box2)
        self.assertEqual(iou, 0.0)
        
    def test_cart_summary(self):
        tracker = GroceryCartTracker(self.config)
        
        # Add test item
        item = DetectedItem(
            label="apple",
            sku="SKU00101",
            confidence=0.8,
            bbox=(10, 10, 50, 50),
            last_seen=1234567890.0,
            confirmed=True
        )
        tracker.cart_inventory["apple_0"] = item
        
        summary = tracker.get_cart_summary()
        self.assertEqual(summary["cart_id"], "test_cart")
        self.assertEqual(summary["item_count"], 1)
        self.assertEqual(len(summary["items"]), 1)
        self.assertEqual(summary["items"][0]["label"], "apple")

if __name__ == '__main__':
    unittest.main()