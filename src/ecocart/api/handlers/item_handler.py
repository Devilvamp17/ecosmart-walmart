"""
EcoCart Item Handler
Business logic for item operations
"""
import logging
from typing import Dict, Any, Optional
from ..models.database import Database


class ItemHandler:
    """Handler for item operations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def add_item(self, cart_id: str, sku: str, label: str, confidence: float) -> Dict[str, Any]:
        """Add item to cart"""
        try:
            # Get or create cart
            cart = self.db.get_or_create_cart(cart_id)
            
            # Add item to cart
            success = cart.add_item(sku, label, confidence)
            
            if success:
                self.logger.info(f"Added item {sku} ({label}) to cart {cart_id}")
                return {
                    "success": True,
                    "message": f"Item {label} added to cart {cart_id}",
                    "cart_summary": cart.get_summary()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to add item {label} to cart {cart_id}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to add item {sku} to cart {cart_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to add item: {str(e)}"
            }
    
    def remove_item(self, cart_id: str, sku: str, label: str) -> Dict[str, Any]:
        """Remove item from cart"""
        try:
            cart = self.db.get_cart(cart_id)
            
            if not cart:
                return {
                    "success": False,
                    "message": f"Cart {cart_id} not found"
                }
            
            success = cart.remove_item(sku)
            
            if success:
                self.logger.info(f"Removed item {sku} ({label}) from cart {cart_id}")
                return {
                    "success": True,
                    "message": f"Item {label} removed from cart {cart_id}",
                    "cart_summary": cart.get_summary()
                }
            else:
                return {
                    "success": False,
                    "message": f"Item {label} not found in cart {cart_id}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to remove item {sku} from cart {cart_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to remove item: {str(e)}"
            }
    
    def get_item_info(self, cart_id: str, sku: str) -> Optional[Dict[str, Any]]:
        """Get item information from cart"""
        try:
            cart = self.db.get_cart(cart_id)
            
            if not cart:
                return None
            
            if sku in cart.items:
                item = cart.items[sku]
                return {
                    "sku": item.sku,
                    "label": item.label,
                    "quantity": item.quantity,
                    "confidence": item.confidence,
                    "added_at": item.added_at,
                    "last_updated": item.last_updated
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get item {sku} from cart {cart_id}: {e}")
            return None
    
    def update_item_quantity(self, cart_id: str, sku: str, quantity: int) -> Dict[str, Any]:
        """Update item quantity in cart"""
        try:
            cart = self.db.get_cart(cart_id)
            
            if not cart:
                return {
                    "success": False,
                    "message": f"Cart {cart_id} not found"
                }
            
            if sku not in cart.items:
                return {
                    "success": False,
                    "message": f"Item {sku} not found in cart {cart_id}"
                }
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                success = cart.remove_item(sku)
                message = f"Item {sku} removed from cart {cart_id}"
            else:
                # Update quantity
                cart.items[sku].quantity = quantity
                cart.total_items = sum(item.quantity for item in cart.items.values())
                success = True
                message = f"Item {sku} quantity updated to {quantity}"
            
            if success:
                self.logger.info(f"Updated item {sku} quantity in cart {cart_id}")
                return {
                    "success": True,
                    "message": message,
                    "cart_summary": cart.get_summary()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to update item {sku} quantity"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to update item {sku} quantity in cart {cart_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to update item quantity: {str(e)}"
            }