import os
from fastapi import FastAPI
from dotenv import load_dotenv

# 1. Cargar el archivo .env inmediatamente para configurar local/nube
load_dotenv()

# 2. Importar los módulos de configuración y arquitectura desglosados
from src.api.config.cors_config import configure_cors
from src.api.config.swagger_config import configure_swagger_security
from src.infrastructure.di.service_container import infrastructure_container

# 3. Importar tus controladores
from src.api.controllers.country_controller import router as country_router
from src.api.controllers.user_controller import router as user_router

# 4. Inicializar la aplicación FastAPI
app = FastAPI(
    title="PIPO API", 
    description="Clean Architecture"
)

# 5. Ejecutar los desgloses modulares (CORS e Inyección de Dependencias)
configure_cors(app)
configure_swagger_security(app)
infrastructure_container(app)

# Registrar controladores
app.include_router(country_router)
app.include_router(user_router)