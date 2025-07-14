import sqlite3
import json

DATABASE_FILE = "ecocart_billing.db"
SKU_MAP_PATH = "/home/himanshu/projects/walmart/config/sku_map.json"

def get_sku_map():
    with open(SKU_MAP_PATH, 'r') as f:
        return json.load(f)

def initialize_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_item_to_bill(item_name):
    sku_map = get_sku_map()
    item_info = sku_map.get(item_name)
    if not item_info:
        print(f"Warning: Item '{item_name}' not found in SKU map.")
        return False

    price = item_info.get("price")
    if price is None:
        print(f"Warning: Price not defined for item '{item_name}'.")
        return False

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO billing (item_name, price) VALUES (?, ?)", (item_name, price))
    conn.commit()
    conn.close()
    return True

def get_total_bill():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(price) FROM billing")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total is not None else 0.0

def get_all_billed_items():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, item_name, price, timestamp FROM billing ORDER BY timestamp DESC")
    items = cursor.fetchall()
    conn.close()
    return items

def remove_item_from_bill(item_id: int):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM billing WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def clear_bill():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM billing")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized and 'billing' table created.")
    # Example usage:
    # add_item_to_bill("apple")
    # add_item_to_bill("orange")
    # print(f"Current total bill: {get_total_bill()}")
    # print("All billed items:", get_all_billed_items())
    # clear_bill()
    # print("Bill cleared. Current total bill:", get_total_bill())
