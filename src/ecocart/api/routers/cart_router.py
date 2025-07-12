# src/ecocart/api/routers/cart_router.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.ecocart.api.handlers import cart_handler

router = APIRouter()

class AddItemRequest(BaseModel):
    cart_id: str
    sku: str
    label: str
    confidence: float
    timestamp: float

class RemoveItemRequest(BaseModel):
    cart_id: str
    sku: str
    label: str
    timestamp: float

@router.post("/add_item")
def add_item(req: AddItemRequest):
    return cart_handler.add_item(
        req.cart_id, req.sku, req.label, req.confidence, req.timestamp
    )

@router.post("/remove_item")
def remove_item(req: RemoveItemRequest):
    return cart_handler.remove_item(
        req.cart_id, req.sku, req.label, req.timestamp
    )

@router.get("/cart/{cart_id}/summary")
def cart_summary(cart_id: str):
    return cart_handler.get_cart_summary(cart_id)
