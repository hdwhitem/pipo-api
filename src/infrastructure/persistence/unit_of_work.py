from motor.motor_asyncio import AsyncIOMotorClient
from src.application.interfaces.iunit_of_work import IUnitOfWork

class MongoUnitOfWork(IUnitOfWork):
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self.session = None

    async def __aenter__(self):
        self.session = await self.client.start_session()
        self.session.start_transaction()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.end_session()
        self.session = None

    async def commit(self):
        await self.session.commit_transaction()

    async def rollback(self):
        await self.session.abort_transaction()
