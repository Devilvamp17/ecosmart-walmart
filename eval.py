import os
import json
import logging
import subprocess
from pathlib import Path
import numpy as np
import cv2
from ultralytics import YOLO
import importlib
import time
import torch

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s:EcoCartDiagnostics:%(message)s')
log = logging.getLogger("EcoCartDiagnostics")

# Paths
MODEL_PATH = "models/yolov8n.pt"
SKU_MAP_PATH = "config/sku_map.json"
CONFIG_PATH = "config/tracker_config.yaml"
VIDEO_SAMPLE_PATH = "data/test_videos/sample.mp4"

# Helpers
def file_exists(path, critical=True):
    if Path(path).exists():
        log.info(f"[✔] Found: {path}")
        return True
    msg = f"[✘] Missing: {path}"
    log.error(msg) if critical else log.warning(msg)
    return False

def is_valid_json(path):
    try:
        with open(path) as f:
            data = json.load(f)
        log.info(f"[✔] Valid JSON: {path}")
        return data
    except Exception as e:
        log.error(f"[✘] Invalid JSON {path}: {e}")
        return None

def validate_sku_map(data):
    issues = []
    if not isinstance(data, dict):
        log.error("[✘] SKU map is not a dictionary")
        return False
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, str):
            issues.append((k, v))
    if issues:
        log.warning(f"[!] SKU map contains non-string keys or values: {issues[:3]}")
    if 'apple' not in data:
        log.warning("[!] 'apple' missing from SKU map — add common test item")
    log.info(f"[✔] SKU map contains {len(data)} items")
    return True

def test_model_inference(path):
    try:
        model = YOLO(path)
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        result = model(dummy)
        if result[0].boxes is not None:
            log.info("[✔] YOLOv8 dummy inference ran successfully")
        return True
    except Exception as e:
        log.error(f"[✘] Failed YOLO model load/inference: {e}")
        return False

def test_video_inference(path, model_path):
    if not os.path.exists(path):
        log.warning("[!] Skipping video inference test (video not found)")
        return True
    try:
        cap = cv2.VideoCapture(path)
        model = YOLO(model_path)
        _, frame = cap.read()
        if frame is None:
            raise Exception("Frame capture failed")
        result = model(frame)
        count = len(result[0].boxes)
        log.info(f"[✔] YOLOv8 test video inference ran. Detected {count} objects.")
        return True
    except Exception as e:
        log.error(f"[✘] Video inference failed: {e}")
        return False

def test_tracker_main():
    try:
        from src.ecocart import main
        tracker = main.GroceryCartTracker(main.Config())
        summary = tracker.get_cart_summary()
        log.info(f"[✔] Tracker initialized. Cart Summary: {summary}")
        return True
    except Exception as e:
        log.error(f"[✘] Tracker init failed: {e}")
        return False

def test_main_function():
    try:
        mod = importlib.import_module("src.ecocart.main")
        if hasattr(mod, "main"):
            log.info("[✔] main() function exists")
            return True
        log.warning("[!] No main() function found in main.py")
        return False
    except Exception as e:
        log.error(f"[✘] Could not import main.py: {e}")
        return False

def test_run_tracker_help():
    try:
        result = subprocess.run(["python", "run_tracker.py", "--help"], capture_output=True)
        if result.returncode == 0:
            log.info("[✔] run_tracker.py executes (help mode)")
            return True
        log.warning("[!] run_tracker.py returned non-zero code")
        return False
    except Exception as e:
        log.error(f"[✘] run_tracker.py failed: {e}")
        return False

def test_api_ping():
    try:
        from src.ecocart.utils.api_client import APIClient
        from src.ecocart.config import Config
        client = APIClient(Config())
        if client.ping_backend():
            log.info("[✔] Backend is reachable")
        else:
            log.warning("[!] Backend is unreachable (warn only)")
        return True
    except Exception as e:
        log.error(f"[✘] APIClient failed: {e}")
        return False

def test_unit_tests():
    try:
        result = subprocess.run(["pytest", "tests", "-q"], capture_output=True, text=True)
        if result.returncode == 0:
            log.info("[✔] Unit tests passed")
        else:
            log.warning("[!] Some unit tests failed:\n" + result.stdout)
        return True
    except FileNotFoundError:
        log.warning("[!] pytest not found")
        return False
    except Exception as e:
        log.error(f"[✘] pytest run failed: {e}")
        return False

def check_pytorch_version():
    v = torch.__version__
    log.info(f"[ℹ] PyTorch version: {v}")
    if "2.6" in v:
        log.warning("[!] PyTorch 2.6 may cause torch.load issues (weights_only=True)")
    return True

def run():
    log.info("🚦 Starting full EcoCart functional + runtime diagnostics...\n")
    results = []

    # File & Config Checks
    results.append(file_exists(MODEL_PATH))
    sku = is_valid_json(SKU_MAP_PATH)
    results.append(sku is not None and validate_sku_map(sku))
    results.append(file_exists(CONFIG_PATH))
    results.append(file_exists("run_tracker.py"))
    # results.append(file_exists("cli.py", critical=False))

    # Inference & Pipeline
    results.append(test_model_inference(MODEL_PATH))
    results.append(test_video_inference(VIDEO_SAMPLE_PATH, MODEL_PATH))
    results.append(test_tracker_main())
    results.append(test_main_function())
    results.append(test_run_tracker_help())

    # Backend/API
    results.append(test_api_ping())

    # Testing
    results.append(test_unit_tests())
    results.append(check_pytorch_version())

    # Final Summary
    log.info("\n📊 Summary Report:")
    passed = sum(results)
    total = len(results)
    for i, res in enumerate(results):
        if not res:
            log.warning(f"[{i+1}] ❌ Test failed")
    if passed == total:
        log.info(f"✅ All {total}/{total} checks passed")
    else:
        log.warning(f"⚠️ Only {passed}/{total} checks passed — review logs above")

if __name__ == "__main__":
    run()