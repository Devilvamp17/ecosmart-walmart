"""
EcoCart Item Router
API endpoints for item operations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from ..state import get_app_state

router = APIRouter()

class AddItemRequest(BaseModel):
    cart_id: str
    sku: str
    label: str
    confidence: float
    timestamp: Optional[float] = None

class RemoveItemRequest(BaseModel):
    cart_id: str
    sku: str
    label: str
    timestamp: Optional[float] = None

class UpdateQuantityRequest(BaseModel):
    cart_id: str
    sku: str
    quantity: int

class ItemResponse(BaseModel):
    success: bool
    message: str
    cart_summary: Optional[Dict[str, Any]] = None

def get_item_handler():
    """Dependency to get item handler"""
    app_state = get_app_state()
    if 'item_handler' not in app_state:
        raise HTTPException(status_code=500, detail="Item handler not initialized")
    return app_state['item_handler']

@router.post("/add_item", response_model=ItemResponse)
async def add_item(request: AddItemRequest, item_handler=Depends(get_item_handler)):
    """Add item to cart"""
    result = item_handler.add_item(
        cart_id=request.cart_id,
        sku=request.sku,
        label=request.label,
        confidence=request.confidence
    )
    
    if result['success']:
        return ItemResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.post("/remove_item", response_model=ItemResponse)
async def remove_item(request: RemoveItemRequest, item_handler=Depends(get_item_handler)):
    """Remove item from cart"""
    result = item_handler.remove_item(
        cart_id=request.cart_id,
        sku=request.sku,
        label=request.label
    )
    
    if result['success']:
        return ItemResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.get("/{cart_id}/{sku}")
async def get_item_info(cart_id: str, sku: str, item_handler=Depends(get_item_handler)):
    """Get item information from cart"""
    item_info = item_handler.get_item_info(cart_id, sku)
    
    if item_info:
        return item_info
    else:
        raise HTTPException(status_code=404, detail=f"Item {sku} not found in cart {cart_id}")

@router.put("/update_quantity", response_model=ItemResponse)
async def update_item_quantity(request: UpdateQuantityRequest, item_handler=Depends(get_item_handler)):
    """Update item quantity in cart"""
    result = item_handler.update_item_quantity(
        cart_id=request.cart_id,
        sku=request.sku,
        quantity=request.quantity
    )
    
    if result['success']:
        return ItemResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result['message'])

# Additional endpoint for direct API client compatibility
@router.post("/add")
async def add_item_simple(request: AddItemRequest, item_handler=Depends(get_item_handler)):
    """Add item to cart (simplified endpoint for API client)"""
    result = item_handler.add_item(
        cart_id=request.cart_id,
        sku=request.sku,
        label=request.label,
        confidence=request.confidence
    )
    
    if result['success']:
        return {"status": "success", "message": result['message']}
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@router.post("/remove")
async def remove_item_simple(request: RemoveItemRequest, item_handler=Depends(get_item_handler)):
    """Remove item from cart (simplified endpoint for API client)"""
    result = item_handler.remove_item(
        cart_id=request.cart_id,
        sku=request.sku,
        label=request.label
    )
    
    if result['success']:
        return {"status": "success", "message": result['message']}
    else:
        raise HTTPException(status_code=400, detail=result['message'])