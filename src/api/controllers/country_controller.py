import os
from fastapi import APIRouter, Depends
from typing import List
from src.domain.collections.gcountry import Gcountry
from src.application.interfaces.imongo_repo import IMongoRepo
from src.infrastructure.persistence.mongo_repo import MongoRepo

router = APIRouter(prefix="/Country", tags=["Country"])

# Contenedor de dependencias (Fábrica)
def get_mongo_repo() -> IMongoRepo:
    conn_str = os.getenv("MONGODB_URL")
    # Retornamos la implementación concreta, cumpliendo el contrato de la interfaz
    return MongoRepo(conn_str)

@router.get("/", response_model=List[Gcountry])
async def country_list_async(repo: IMongoRepo = Depends(get_mongo_repo)):
    # El controlador solo conoce los métodos definidos en IMongoRepo
    result = await repo.get_country_list_async()
    return result