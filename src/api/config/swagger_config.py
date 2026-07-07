from fastapi import FastAPI

def configure_swagger_security(app: FastAPI) -> None:
    app.swagger_ui_parameters = {"withCredentials": True}
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
            
        # Generamos el esquema base
        openapi_schema = app.openapi_schema if app.openapi_schema else None
        # Forzamos la generación inicial si no existe
        from fastapi.openapi.utils import get_openapi
        openapi_schema = get_openapi(
            title=app.title,
            version="1.0.0",
            description=app.description,
            routes=app.routes,
        )
        
        # Inyectamos el esquema de seguridad Bearer (Idéntico al AddSecurityDefinition de .NET)
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Introduce el token JWT generado en el Login (sin la palabra Bearer delante)."
            }
        }
        
        # Aplicamos la seguridad de forma global a todos los endpoints de la documentación
        openapi_schema["security"] = [{"BearerAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
