# 🛒 EcoSmart Walmart – Vision Module

**EcoSmart Walmart** is a smart retail system designed to provide real-time product detection, identification, and sustainability analysis in a shopping environment.  
This repository contains the **vision component**, which powers object detection and tracking in smart shopping carts using YOLOv8, ByteTrack, and object re-identification.

---

## 📦 Repository Structure

```
ecosmart-walmart/
├── models/                 # Trained YOLOv8 weights
├── src/
│   └── ecocart/
│       ├── main.py         # Entry point for the vision system
│       ├── detector.py     # Handles object detection (YOLOv8)
│       ├── tracker.py      # ByteTrack/DeepSort for multi-object tracking
│       ├── reid.py         # Re-identification logic for item consistency
│       ├── utils.py        # Utility functions
│       └── config.py       # Configuration for paths, thresholds, etc.
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies
├── eval.py                 # Diagnostic checker for all vision components
└── README.md               # This file
```

---

## 🔍 What This Module Does

- Detects grocery items in real-time using YOLOv8.
- Tracks items even if they move within the cart using ByteTrack.
- Re-identifies previously seen items (helps with quantity and movement tracking).
- Sends real-time API calls to the backend when items are added or removed.
- Designed to integrate with sustainability analysis and front-end display.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Devilvamp17/ecosmart-walmart.git
cd ecosmart-walmart
```

### 2. Install Dependencies

We recommend using a Python virtual environment.

```bash
pip install -r requirements.txt
```

### 3. Download Model Weights

Download or train your YOLOv8 weights and place them inside the `models/` directory. Example:

```
models/
├── yolov8n.pt
├── yolov8n_reid.pt
```

---

## ▶️ Running the Vision System

To start detection and tracking:

```bash
python src/ecocart/main.py --video_path <your_video.mp4>
```

You can also use webcam input:

```bash
python src/ecocart/main.py --video_path 0
```

---

## ⚙️ Configuration

Update configuration values in `config.py`:

```python
@dataclass
class Config:
    MODEL_PATH: str = "models/yolov8n.pt"
    CONFIDENCE_THRESHOLD: float = 0.6
    IOU_THRESHOLD: float = 0.5
    CART_ID: str = "cart_001"
    BACKEND_URL: str = "http://localhost:8000"
    LOG_TO_FILE = False
```

You can set the backend URL, cart ID, model paths, and detection thresholds.

---

## ✅ Evaluation and Diagnostics

To verify all modules are working correctly, run:

```bash
python eval.py
```

This will:

- Load YOLOv8 weights and check compatibility
- Verify tracker and ReID module initialization
- Check SKU mapping availability
- Ping the FastAPI backend
- Run inference on a test frame

---

## 🧠 Features & Roadmap

✅ YOLOv8-based detection  
✅ ByteTrack-based object tracking  
✅ Item re-identification and ID persistence  
✅ API-based item add/remove updates  
✅ Modular and extensible architecture

🔜 Planned Enhancements:

- [ ] Frame skipping for improved real-time performance
- [ ] Object quantity tracking (e.g., 2 apples)
- [ ] Video recording support
- [ ] Better ReID embeddings for high accuracy

---

## 🔗 Integration

This module communicates with the EcoCart **FastAPI backend** (`localhost:8000` by default). It sends POST requests when:

- An item is added to the cart
- An item is removed from the cart
- A previously seen item is re-identified

This ensures accurate item tracking across the entire cart session.

---

## 🧪 Example Output (Terminal Logs)

```
[INFO] Apple detected and added to cart.
[INFO] Milk detected and added to cart.
[INFO] Tomato removed from cart.
[INFO] Re-identified previously seen item: Apple.
```

---

## 🛠️ Contributors

- [@Devilvamp17](https://github.com/Devilvamp17)
- [@HimanshuSardana](https://github.com/HimanshuSardana)
---
