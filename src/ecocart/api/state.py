from collections import defaultdict
from typing import Dict, List

cart_db: Dict[str, List[dict]] = defaultdict(list)

def get_app_state():
    return {
        "carts": list(cart_db.keys()),
        "total_items": sum(len(items) for items in cart_db.values())
    }
