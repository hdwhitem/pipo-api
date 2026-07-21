# src/infrastructure/di/service_container.py
import os
from fastapi import FastAPI, Request
from src.infrastructure.persistence.mongo_repo import MongoRepo
from src.infrastructure.services.pdf.pdf_service_impl import PdfService
from src.application.interfaces.imongo_repo import IMongoRepo
from src.application.interfaces.ipdf_service import IPdfService

def infrastructure_container(app: FastAPI) -> None:
    connection_string = os.getenv("MONGODB_URL")
    app.state.repo = MongoRepo(connection_string=connection_string)
    app.state.pdf_service = PdfService()

def get_repo(request: Request) -> IMongoRepo:
    return request.app.state.repo

def get_pdf_service(request: Request) -> IPdfService:
    return request.app.state.pdf_service
