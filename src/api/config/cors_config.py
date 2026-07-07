from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200", 
            "https://localhost:4200", 
            "http://localhost:7198"
        ],
        allow_credentials=True, # Crucial para el intercambio de cookies HttpOnly
        allow_methods=["*"],
        allow_headers=["*"],
    )