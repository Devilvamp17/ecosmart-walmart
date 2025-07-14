# src/ecocart/api/app.py

import json
from fastapi import FastAPI
from src.ecocart.api.routers import cart_router, health_router
from src.ecocart.database import initialize_db
from src.vector_db import VectorDB

def create_app() -> FastAPI:
    app = FastAPI(title="EcoCart API")

    @app.on_event("startup")
    async def startup_event():
        initialize_db()
        # Load sku_map.json and initialize VectorDB
        with open("/home/himanshu/projects/walmart/config/sku_map.json", "r") as f:
            sku_map_data = json.load(f)
        app.state.vector_db = VectorDB(sku_map_data)

    app.include_router(cart_router.router)
    app.include_router(health_router.router)

    return app
