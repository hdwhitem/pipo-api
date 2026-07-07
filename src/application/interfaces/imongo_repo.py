from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.collections.gcountry import Gcountry
from src.domain.dtos.register_dto import RegisterUserDto
from src.domain.dtos.login_dto import LoginDto

class IMongoRepo(ABC):
    
    @abstractmethod
    async def get_country_list_async(self) -> List[Gcountry]:
        """Contrato para obtener la lista de países"""
        pass
    
    @abstractmethod
    async def register_user_async(self, dto: RegisterUserDto) -> Dict[str, Any]:
        """Contrato para el registro de un usuario"""
        pass

    @abstractmethod
    async def login_user_async(self, dto: LoginDto) -> Dict[str, Any]:
        """Contrato para el login de un usuario"""
        pass