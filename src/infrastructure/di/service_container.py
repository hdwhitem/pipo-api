# src/infrastructure/di/service_container.py
import os
from fastapi import FastAPI
from src.infrastructure.persistence.mongo_repo import MongoRepo

def infrastructure_container(app: FastAPI) -> None:
    # Lee la URL de la base de datos desde el entorno (.env local o nube)
    connection_string = os.getenv("MONGODB_URL")
    
    # Registramos la instancia única (Singleton) en el estado global de la app
    app.state.repo = MongoRepo(connection_string=connection_string)