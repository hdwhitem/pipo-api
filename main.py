from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os

from src.core.exceptions import DomainException
from src.api.config.cors_config import configure_cors
from src.api.config.swagger_config import configure_swagger_security
from src.infrastructure.di.service_container import setup_infrastructure
from src.api.controllers.country_controller import router as country_router
from src.api.controllers.user_controller import router as user_router
from src.api.controllers.pdf_controller import router as pdf_router
from src.api.controllers.invitation_controller import router as invitation_router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection_string = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(connection_string)
    app.state.db_client = client
    setup_infrastructure(app, client)
    yield
    client.close()

app = FastAPI(
    title="PIPO API", 
    description="Clean Architecture",
    lifespan=lifespan
)

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

configure_cors(app)
configure_swagger_security(app)

app.include_router(country_router)
app.include_router(user_router)
app.include_router(pdf_router)
app.include_router(invitation_router)
