# src/ecocart/api/routers/cart_router.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.ecocart.api.handlers import cart_handler
from src.ecocart.database import (
    get_total_bill,
    get_all_billed_items,
    clear_bill,
    remove_item_from_bill,
)
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(
    directory="/home/himanshu/projects/walmart/src/ecocart/api/templates"
)


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
    return cart_handler.remove_item(req.cart_id, req.sku, req.label, req.timestamp)


@router.get("/cart/{cart_id}/summary")
def cart_summary(cart_id: str):
    return cart_handler.get_cart_summary(cart_id)


@router.get("/bill")
async def get_bill(request: Request):
    total = get_total_bill()
    items = get_all_billed_items()

    items_with_info = []
    for item in items:
        item_name = item[1]  # Assuming item name is at index 1
        vector_db = request.app.state.vector_db
        # item_info = vector_db.query(item_name)
        items_with_info.append((
            *item,
            "",
        ))  # Append item_info to the existing item tuple

    return {"total_bill": total, "items": items_with_info}


@router.post("/bill/clear")
def clear_current_bill():
    clear_bill()
    return {"status": "success", "message": "Bill cleared."}


@router.post("/bill/remove/{item_id}")
def remove_billed_item(item_id: int):
    remove_item_from_bill(item_id)
    return {"status": "success", "message": f"Item {item_id} removed."}


@router.get("/item_info/{item_name}")
async def get_item_info(item_name: str, request: Request):
    vector_db = request.app.state.vector_db
    info = vector_db.query(item_name)
    return {"item_name": item_name, "info": info}


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
