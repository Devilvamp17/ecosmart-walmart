# src/ecocart/api/handlers/cart_handler.py

from typing import Dict
from src.ecocart.api.state import cart_db
import time
from src.ecocart.database import add_item_to_bill

def add_item(cart_id: str, sku: str, label: str, confidence: float, timestamp: float) -> Dict:
    item = {
        "sku": sku,
        "label": label,
        "confidence": confidence,
        "timestamp": timestamp
    }
    cart_db[cart_id].append(item)
    add_item_to_bill(label) # Add item to the SQLite database
    return {"status": "success", "message": f"Item {label} added."}


def remove_item(cart_id: str, sku: str, label: str, timestamp: float) -> Dict:
    if cart_id not in cart_db:
        return {"status": "error", "message": "Cart not found"}

    original_len = len(cart_db[cart_id])
    cart_db[cart_id] = [
        item for item in cart_db[cart_id]
        if item["sku"] != sku or item["label"] != label
    ]
    if len(cart_db[cart_id]) == original_len:
        return {"status": "warning", "message": f"Item {label} not found"}

    return {"status": "success", "message": f"Item {label} removed."}

def get_cart_summary(cart_id: str) -> Dict:
    items = cart_db.get(cart_id, [])
    return {
        "cart_id": cart_id,
        "timestamp": time.time(),
        "item_count": len(items),
        "items": items
    }
