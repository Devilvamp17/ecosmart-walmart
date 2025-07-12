# src/ecocart/api/main.py

import uvicorn
from src.ecocart.api.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.ecocart.api.main:app", host="0.0.0.0", port=8000, reload=True)
