from abc import ABC, abstractmethod
from typing import List
from src.domain.collections.gcountry import Gcountry

class IMongoRepo(ABC):
    
    @abstractmethod
    async def get_country_list_async(self) -> List[Gcountry]:
        """Contrato para obtener la lista de países"""
        pass