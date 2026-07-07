import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

from src.application.interfaces.imongo_repo import IMongoRepo
from src.domain.collections.gcountry import Gcountry
from src.domain.collections.guser import Guser
from src.domain.dtos.register_dto import RegisterUserDto
from src.domain.dtos.login_dto import LoginDto

class MongoRepo(IMongoRepo):  # Implementa la interfaz heredando de ella
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client["Shop"]
        self.country_collection = self.db["Gcountry"]
        self.user_collection = self.db["Guser"]

        # Configuración JWT
        self.jwt_key = os.getenv("JWT_KEY")
        self.jwt_issuer = os.getenv("JWT_ISSUER")
        self.jwt_audience = os.getenv("JWT_AUDIENCE")
        self.duration = int(os.getenv("JWT_DURATION_MINUTES", 60))

    async def get_country_list_async(self) -> List[Gcountry]:
        countries = []
        cursor = self.country_collection.find({}).sort("name", 1)
        async for document in cursor:
            countries.append(Gcountry(**document))
        return countries

    async def register_user_async(self, dto: RegisterUserDto) -> Dict[str, Any]:
        existing = await self.user_collection.find_one({"UserEmail": dto.email})
        if existing:
            return {"flag": False, "message": "User already exist"}

        # Hashing de la contraseña usando bcrypt (idéntico a tu librería de .NET)
        hashed_password = bcrypt.hashpw(dto.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = {
            "UserName": dto.name,
            "UserLastName": dto.lastName,
            "UserEmail": dto.email,
            "UserPassword": hashed_password
        }
        await self.user_collection.insert_one(new_user)
        return {"flag": True, "message": "registration completed"}

    async def login_user_async(self, dto: LoginDto) -> Dict[str, Any]:
        user_dict = await self.user_collection.find_one({"UserEmail": dto.email})
        if not user_dict:
            return {"flag": False, "message": "user not found", "token": None}

        # Validación del hash de la contraseña
        if not bcrypt.checkpw(dto.password.encode('utf-8'), user_dict["UserPassword"].encode('utf-8')):
            return {"flag": False, "message": "invalid credentials", "token": None}

        # Generación del token pasando los claims solicitados
        token = self.generate_jwt_token(str(user_dict["_id"]), user_dict["UserName"], user_dict["UserEmail"])
        
        return {
            "flag": True,
            "message": "Login successfully",
            "token": token,
            "name": user_dict["UserName"],
            "email": user_dict["UserEmail"]
        }

    def generate_jwt_token(self, user_id: str, name: str, email: str) -> str:
        try:
            minutos = int(self.duration)
        except Exception:
            minutos = 1440

        ahora_timestamp = int(datetime.now(timezone.utc).timestamp())

        expiracion_timestamp = ahora_timestamp + (minutos * 60)

        payload = {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier": user_id,
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": name,
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": email,
            "iss": self.jwt_issuer,
            "aud": "self.jwt_audience",
            "exp": expiracion_timestamp
        }
        
        return jwt.encode(payload, self.jwt_key, algorithm="HS256")