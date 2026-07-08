import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app: FastAPI) -> None:
    
    raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")

    origins_list = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=True, # Crucial para el intercambio de cookies HttpOnly
        allow_methods=["*"],
        allow_headers=["*"],
    )