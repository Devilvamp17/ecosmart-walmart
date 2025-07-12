from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # Model Configuration
    MODEL_PATH: str = "models/yolov8n.pt"
    CONFIDENCE_THRESHOLD: float = 0.4
    IOU_THRESHOLD: float = 0.5
    LOG_TO_FILE: bool = False
    LOG_LEVEL: str = "INFO"  

    # Cart Configuration
    CART_ID: str = "cart_001"
    BACKEND_URL: str = "http://localhost:8000"
    LABEL_MAP_PATH: str = "config/sku_map.json"
    
    # Detection Settings
    REMOVAL_TIMEOUT: int = 3  # seconds
    STABILIZATION_FRAMES: int = 5  # frames to confirm detection
    FRAME_SKIP: int = 2  # process every nth frame
    
    # API Settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: float = 1.0
    API_TIMEOUT: int = 5
    
    # Video Settings
    VIDEO_SOURCE: int = 0  # 0 for webcam, or path to video file
    DISPLAY_WINDOW: bool = True
