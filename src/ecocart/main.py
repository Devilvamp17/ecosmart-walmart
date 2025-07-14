import cv2
import time
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from ultralytics import YOLO
import numpy as np

from src.ecocart.config import Config
from src.ecocart.utils.api_client import APIClient

@dataclass
class DetectedItem:
    label: str
    sku: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    last_seen: float
    detection_count: int = 0
    confirmed: bool = False
    quantity: int = 1
    track_id: Optional[int] = None  

class GroceryCartTracker:
    def __init__(self, config: Config):
        self.config = config
        self.setup_logging()
        self.load_dependencies()
        self.reset_state()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        handlers = [logging.StreamHandler()]
        
        if self.config.LOG_TO_FILE:
            handlers.append(logging.FileHandler(f'logs/cart_{self.config.CART_ID}.log'))
            
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format=log_format,
            handlers=handlers
        )
        self.logger = logging.getLogger(__name__)
        
    def load_dependencies(self):
        """Load model and SKU mappings"""
        try:
            # Load SKU mapping
            with open(self.config.LABEL_MAP_PATH, "r") as f:
                self.label_to_sku = json.load(f)
            self.logger.info(f"Loaded {len(self.label_to_sku)} SKU mappings")
            
            # Load YOLO model
            self.model = YOLO(self.config.MODEL_PATH)
            self.logger.info(f"Loaded model: {self.config.MODEL_PATH}")
            
            # Initialize API client
            self.api_client = APIClient(self.config)
            
            # Test backend connection
            if not self.api_client.ping_backend():
                self.logger.warning("Backend is not reachable. API calls will fail.")
            else:
                self.logger.info("Backend connection successful")
                
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load dependencies: {e}")
            raise
            
    def reset_state(self):
        """Reset tracking state"""
        self.next_track_id = 1
        self.track_id_map = {}  
        self.cart_inventory: Dict[str, DetectedItem] = {}
        self.detection_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.config.STABILIZATION_FRAMES)
        )
        self.frame_count = 0
        
    def calculate_iou(self, box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union for bounding boxes"""
        x1, y1, x2, y2 = box1
        x1_p, y1_p, x2_p, y2_p = box2
        
        # Calculate intersection
        xi1 = max(x1, x1_p)
        yi1 = max(y1, y1_p)
        xi2 = min(x2, x2_p)
        yi2 = min(y2, y2_p)
        
        if xi2 <= xi1 or yi2 <= yi1:
            return 0.0
            
        intersection = (xi2 - xi1) * (yi2 - yi1)
        
        # Calculate union
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x2_p - x1_p) * (y2_p - y1_p)
        union = box1_area + box2_area - intersection
        
        return intersection / union if union > 0 else 0.0
        
    def is_same_detection(self, new_bbox: Tuple[int, int, int, int], existing_item: DetectedItem) -> bool:
        """Check if new detection is the same as existing item"""
        return self.calculate_iou(new_bbox, existing_item.bbox) > self.config.IOU_THRESHOLD
        
    def add_item_to_cart(self, item: DetectedItem) -> bool:
        """Add item to cart via API"""
        success = self.api_client.add_item(
            self.config.CART_ID,
            item.sku,
            item.label,
            item.confidence
        )
        
        if success:
            self.logger.info(f"[+] Added: {item.label} ({item.sku}) - Confidence: {item.confidence:.2f}")
        else:
            self.logger.error(f"Failed to add item: {item.label}")
            
        return success
            
    def remove_item_from_cart(self, item: DetectedItem) -> bool:
        """Remove item from cart via API"""
        success = self.api_client.remove_item(
            self.config.CART_ID,
            item.sku,
            item.label
        )
        
        if success:
            self.logger.info(f"[-] Removed: {item.label} ({item.sku})")
        else:
            self.logger.error(f"Failed to remove item: {item.label}")
            
        return success
            
    def process_detections(self, results, frame_time: float):
        """Process YOLO detections and update cart state"""
        current_detections = {}
        
        # Parse detections
        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < self.config.CONFIDENCE_THRESHOLD:
                continue
                
            cls = int(box.cls[0])
            label = self.model.names[cls]
            
            if label not in self.label_to_sku:
                continue
                
            bbox = tuple(map(int, box.xyxy[0]))
            sku = self.label_to_sku[label]["sku"]
            
            # Check if this detection matches an existing item
            matched_key = None
            for key, existing_item in self.cart_inventory.items():
                if existing_item.label == label and self.is_same_detection(bbox, existing_item):
                    matched_key = key
                    break
                    
            if matched_key:
                # Update existing item
                item = self.cart_inventory[matched_key]
                item.bbox = bbox
                item.confidence = max(item.confidence, conf)
                item.last_seen = frame_time
                item.detection_count += 1
                current_detections[matched_key] = item
            else:
                # New detection
                item_key = f"{label}_{len(current_detections)}"
                item = DetectedItem(
                    label=label,
                    sku=sku,
                    confidence=conf,
                    bbox=bbox,
                    last_seen=frame_time,
                    detection_count=1
                )
                current_detections[item_key] = item
                
        # Update detection history and confirm items
        for key, item in current_detections.items():
            self.detection_history[key].append(frame_time)
            
            # Confirm item if we've seen it enough times
            if (not item.confirmed and 
                len(self.detection_history[key]) >= self.config.STABILIZATION_FRAMES):
                
                item.confirmed = True
                self.cart_inventory[key] = item
                self.add_item_to_cart(item)
                
        # Handle removals
        to_remove = []
        for key, item in list(self.cart_inventory.items()):
            if key not in current_detections:
                if frame_time - item.last_seen > self.config.REMOVAL_TIMEOUT:
                    to_remove.append(key)
            else:
                # Update existing item
                self.cart_inventory[key] = current_detections[key]
                
        for key in to_remove:
            item = self.cart_inventory[key]
            if self.remove_item_from_cart(item):
                del self.cart_inventory[key]
                if key in self.detection_history:
                    del self.detection_history[key]
                    
    def draw_annotations(self, frame: np.ndarray, results) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        annotated_frame = frame.copy()
        
        # Draw all detections
        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < self.config.CONFIDENCE_THRESHOLD:
                continue
                
            cls = int(box.cls[0])
            label = self.model.names[cls]
            
            if label not in self.label_to_sku:
                continue
                
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            sku = self.label_to_sku[label]["sku"]
            
            # Color based on confirmation status
            color = (0, 255, 0) if any(item.confirmed and item.label == label 
                                    for item in self.cart_inventory.values()) else (0, 165, 255)
            
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Label with confidence and SKU
            label_text = f"{label} ({sku}) {conf:.2f}"
            cv2.putText(annotated_frame, label_text, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                       
        # Draw cart inventory summary
        y_offset = 30
        cv2.putText(annotated_frame, f"Cart: {self.config.CART_ID}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_offset += 25
        cv2.putText(annotated_frame, f"Items: {len(self.cart_inventory)}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                   
        return annotated_frame
        
    def run(self, video_source: Optional[int] = None):
        """Main inference loop"""
        if video_source is None:
            video_source = self.config.VIDEO_SOURCE
            
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            self.logger.error("Failed to open video source")
            return
            
        self.logger.info(f"Starting inference for cart {self.config.CART_ID}")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.logger.error("Frame capture failed")
                    break
                    
                self.frame_count += 1
                
                # Skip frames for performance
                if self.frame_count % self.config.FRAME_SKIP != 0:
                    continue
                    
                frame_time = time.time()
                
                # Run inference
                results = self.model(frame)[0]
                
                # Process detections
                self.process_detections(results, frame_time)
                
                # Draw annotations and display
                if self.config.DISPLAY_WINDOW:
                    annotated_frame = self.draw_annotations(frame, results)
                    cv2.imshow(f"EcoCart - {self.config.CART_ID}", annotated_frame)
                    
                    if cv2.waitKey(1) == ord("q"):
                        break
                        
        except KeyboardInterrupt:
            self.logger.info("Stopping inference...")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
    def get_cart_summary(self) -> dict:
        return {
            "cart_id": self.config.CART_ID,
            "timestamp": time.time(),
            "item_count": len(self.cart_inventory),
            "items": [
                {
                    "label": item.label,
                    "sku": item.sku,
                    "confidence": item.confidence,
                    "detection_count": item.detection_count,
                    "quantity": item.quantity
                }
                for item in self.cart_inventory.values()
            ]
        }
def main():
    """Test entry point for diagnostics"""
    from src.ecocart.config import Config
    tracker = GroceryCartTracker(Config())
    
    summary = tracker.get_cart_summary()
    print("EcoCart initialized successfully.")
    print("Cart Summary:", summary)
