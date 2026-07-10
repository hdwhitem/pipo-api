from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Variables de entorno
    CLOUDINARY_BASE_URL: str = "https://res.cloudinary.com/dclw4ncmc/image/upload/ADICON"
    DUMMY_IMAGE_NAME: str = "CRYSTAL_BIANCO_pc4ctw.png"
    
    # Puedes añadir más variables según las necesites
    # APP_NAME: str = "My FastAPI Clean Architecture"
    # DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

# Instancia única (Singleton) para exportar a toda la aplicación
settings = Settings()