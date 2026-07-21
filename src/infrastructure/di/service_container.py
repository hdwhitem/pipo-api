# src/infrastructure/di/service_container.py
import os
from fastapi import FastAPI, Request
from src.infrastructure.persistence.mongo_repo import MongoRepo
from src.infrastructure.services.pdf.pdf_service_impl import PdfService
from src.application.interfaces.imongo_repo import IMongoRepo
from src.application.interfaces.ipdf_service import IPdfService

from motor.motor_asyncio import AsyncIOMotorClient
from src.infrastructure.persistence.unit_of_work import MongoUnitOfWork
from src.application.interfaces.iunit_of_work import IUnitOfWork

def setup_infrastructure(app: FastAPI, client: AsyncIOMotorClient) -> None:
    # Usamos el cliente compartido inyectado desde el lifespan
    app.state.repo = MongoRepo(client=client) # Necesitamos ajustar MongoRepo también
    app.state.pdf_service = PdfService()

def get_repo(request: Request) -> IMongoRepo:
    return request.app.state.repo

def get_pdf_service(request: Request) -> IPdfService:
    return request.app.state.pdf_service

def get_uow(request: Request) -> IUnitOfWork:
    return MongoUnitOfWork(request.app.state.db_client)
