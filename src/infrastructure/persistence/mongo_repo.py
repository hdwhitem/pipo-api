from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from src.application.interfaces.imongo_repo import IMongoRepo
from src.domain.collections.gcountry import Gcountry

class MongoRepo(IMongoRepo):  # Implementa la interfaz heredando de ella
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client["Shop"]
        self.collection = self.db["Gcountry"]

    async def get_country_list_async(self) -> List[Gcountry]:
        countries = []
        cursor = self.collection.find({}).sort("name", 1)
        async for document in cursor:
            countries.append(Gcountry(**document))
        return countries