import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from src.application.interfaces.imongo_repo import IMongoRepo
from src.domain.collections.gbank_account import GBankAccount
from src.domain.collections.gcountry import Gcountry
from src.domain.collections.gexporter import GExporter
from src.domain.collections.gmanufacturer import GManufacturer
from src.domain.collections.gsupplier import GSupplier
from src.domain.collections.ginvitation import GInvitation
from src.domain.collections.guser import Guser
from src.domain.collections.gproforma_number import GProformaNumber
from src.domain.collections.gorder import GOrder
from src.domain.collections.gconsignee import GConsignee
from src.domain.dtos.register_dto import RegisterUserDto
from src.domain.dtos.login_dto import LoginDto

class MongoRepo(IMongoRepo):  # Implementa la interfaz heredando de ella
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client["Shop"]
        self.country_collection = self.db["Gcountry"]
        self.user_collection = self.db["Guser"]
        self._proforma = self.db["GProformaNumber"]
        self._order = self.db["GOrder"]
        self._consignee = self.db["Gconsignee"]
        self._supplier = self.db["Gsupplier"]
        self._exporter = self.db["Gexporter"]
        self._manufacturer = self.db["Gmanufacturer"]
        self._bank = self.db["GbankAccount"]
        self._invitation = self.db["Ginvitation"]


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

        aud_value = self.jwt_audience.strip() if self.jwt_audience else "localhost"

        payload = {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier": user_id,
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": name,
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": email,
            "iss": self.jwt_issuer,
            "aud": aud_value,
            "exp": expiracion_timestamp
        }

        return jwt.encode(payload, self.jwt_key, algorithm="HS256")
    
    
    async def get_proforma_number(self) -> int:
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "CurrentProforma": {"$max": "$Count"}
                }
            }
        ]

        cursor = self._proforma.aggregate(pipeline)
        result_list = await cursor.to_list(length=1)

        if result_list and "CurrentProforma" in result_list[0] and result_list[0]["CurrentProforma"] is not None:
            current_proforma = result_list[0]["CurrentProforma"]
            new_count = int(current_proforma) + 1

            new_proforma = GProformaNumber(
                count=new_count,
                created_date=datetime.now(timezone.utc)
            )
            
            await self._proforma.insert_one(
                new_proforma.model_dump(by_alias=True, exclude_none=True)
            )
            return new_count
        else:
            new_count = 198
            new_proforma = GProformaNumber(
                count=new_count,
                created_date=datetime.now(timezone.utc)
            )
            
            await self._proforma.insert_one(
                new_proforma.model_dump(by_alias=True, exclude_none=True)
            )
            print(f"No result found. New proforma: {new_proforma.count}")
            return new_count
        
    async def save_order(self, order: GOrder) -> GOrder:
        existing_order = await self._order.find_one({"pi_number": order.pi_number})

        if existing_order is None:
            order_data = order.model_dump(by_alias=True, exclude_none=True)
            result = await self._order.insert_one(order_data)

            order.id = str(result.inserted_id)

        return order
    
    async def update_pi_number(self, pi: int) -> int:
        # Busca si ya existe un documento con ese 'count'
        get_proforma = await self._proforma.find_one({"count": pi})
        now_utc = datetime.now(timezone.utc)

        if get_proforma is None:
            # Caso Insert: si no existe, creamos el nuevo registro
            new_proforma = GProformaNumber(
                count=pi,
                created_date=now_utc
            )
            await self._proforma.insert_one(
                new_proforma.model_dump(by_alias=True, exclude_none=True)
            )
            return pi
        else:
            # Caso Update: actualizamos la fecha del documento existente
            doc_id = get_proforma["_id"]
            
            result = await self._proforma.update_one(
                {"_id": doc_id},
                {"$set": {"created_date": now_utc}}
            )

            # Si se modificó el documento (o si ya tenía exactamente ese valor)
            if result.modified_count > 0 or result.matched_count > 0:
                return pi
                
            return 0
        
    async def get_consignee_by_id(self, consignee_id: str) -> Optional[GConsignee]:
        
        if ObjectId.is_valid(consignee_id):
            
            doc = await self._consignee.find_one({"_id": ObjectId(consignee_id)})
            
            if doc:
                return GConsignee(**doc)

        return None
    
    async def get_supplier_by_id(self, supplier_id: str) -> Optional[GSupplier]:
        doc = await self._supplier.find_one({"SupplierId": supplier_id})
        
        if doc:
            return GSupplier(**doc)
            
        return None
    
    async def get_exporter_by_id(self, exporter_id: str) -> Optional[GExporter]:
        # Valida que el string sea un ObjectId de Mongo válido (reemplaza a rg.IsMatch)
        if ObjectId.is_valid(exporter_id):
            doc = await self._exporter.find_one({"_id": ObjectId(exporter_id)})
            
            if doc:
                # Instancia y retorna el modelo Pydantic
                return GExporter(**doc)

        return None
    
    async def get_manufacturer_by_id(self, manufacturer_id: str) -> Optional[GManufacturer]:
        # Valida que sea un ObjectId de MongoDB válido (reemplaza a rg.IsMatch)
        if ObjectId.is_valid(manufacturer_id):
            doc = await self._manufacturer.find_one({"_id": ObjectId(manufacturer_id)})
            
            if doc:
                # Convierte el diccionario retornado por Mongo al objeto Pydantic GManufacturer
                return GManufacturer(**doc)

        return None
    
    async def get_bank_account_by_id(self, bank_account_id: str) -> Optional[GBankAccount]:
        # Valida si la cadena es un ObjectId de MongoDB válido (reemplaza a rg.IsMatch)
        if ObjectId.is_valid(bank_account_id):
            doc = await self._bank.find_one({"_id": ObjectId(bank_account_id)})
            
            if doc:
                # Instancia y mapea el diccionario de Mongo al objeto Pydantic GBankAccount
                return GBankAccount(**doc)

        return None
    
    async def create_invitation_async(self, invitation: GInvitation) -> GInvitation:
        """
        Registra una nueva invitación en MongoDB generada por el administrador.
        """
        # Convertimos el modelo Pydantic a diccionario compatible con Mongo
        invitation_data = invitation.model_dump(by_alias=True, exclude_none=True)
        result = await self._invitation.insert_one(invitation_data)
        
        # Asignamos el ID generado de vuelta al objeto
        invitation.id = str(result.inserted_id)
        return invitation

    async def verify_and_use_invitation_async(self, code_str: str) -> Dict[str, Any]:
        """
        Valida que un código exista, no haya sido usado y no esté expirado.
        Si es válido, lo marca como utilizado (used = True) en una sola operación atómica.
        """
        now_utc = datetime.now(timezone.utc)

        # Buscamos el código activo y que no haya expirado
        # Usamos update_one con filtros estrictos para evitar condiciones de carrera (Race Conditions)
        result = await self._invitation.update_one(
            {
                "code": code_str,
                "used": False,
                "expires_at": {"$gt": now_utc}
            },
            {
                "$set": {
                    "used": True,
                    "used_at": now_utc
                }
            }
        )

        if result.modified_count > 0:
            return {"valid": True, "message": "Invitation code accepted"}
        
        # Si no modificó nada, investigamos por qué falló para dar un mensaje claro
        existing = await self._invitation.find_one({"code": code_str})
        if not existing:
            return {"valid": False, "message": "Invalid invitation code"}
        if existing["used"]:
            return {"valid": False, "message": "This code has already been used"}
        if existing["expires_at"] <= now_utc:
            return {"valid": False, "message": "This code has expired"}

        return {"valid": False, "message": "Verification failed"}