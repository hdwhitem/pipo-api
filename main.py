from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.core.exceptions import DomainException

# 1. Cargar el archivo .env inmediatamente para configurar local/nube
load_dotenv()

# 2. Importar los módulos de configuración y arquitectura desglosados
from src.api.config.cors_config import configure_cors
from src.api.config.swagger_config import configure_swagger_security
from src.infrastructure.di.service_container import infrastructure_container

# 3. Importar tus controladores
from src.api.controllers.country_controller import router as country_router
from src.api.controllers.user_controller import router as user_router
from src.api.controllers.pdf_controller import router as pdf_router
from src.api.controllers.invitation_controller import router as invitation_router

# 4. Inicializar la aplicación FastAPI
app = FastAPI(
    title="PIPO API", 
    description="Clean Architecture"
)

# Exception Handlers
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

# 5. Ejecutar los desgloses modulares (CORS e Inyección de Dependencias)
configure_cors(app)
configure_swagger_security(app)
infrastructure_container(app)

# Registrar controladores
app.include_router(country_router)
app.include_router(user_router)
app.include_router(pdf_router)
app.include_router(invitation_router)