import os
from fastapi import FastAPI
from dotenv import load_dotenv  # <-- 1. Importa la librería

# 2. Carga el archivo .env que está en la raíz
load_dotenv()

from src.api.controllers.country_controller import router as country_router

app = FastAPI(title="Clean Architecture en FastAPI Cloud")

# Registrar controladores
app.include_router(country_router)