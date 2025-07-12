# src/ecocart/api/app.py

from fastapi import FastAPI
from src.ecocart.api.routers import cart_router, health_router

def create_app() -> FastAPI:
    app = FastAPI(title="EcoCart API")

    app.include_router(cart_router.router)
    app.include_router(health_router.router)

    return app
