from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorClientSession
from aioredis import Redis
from typing import Optional


class DBProvider:
    def __init__(
        self,
        mongo_connection: Optional[AsyncIOMotorClient],
        redis_connection: Optional[Redis],
    ):

        self._mongo_connection = mongo_connection
        self._redis_connection = redis_connection
        self._mongo_session: Optional[AsyncIOMotorClientSession] = None
        self._redis_session = None

    def get_redis(self) -> Redis:
        return self._redis_connection

    def get_redis_session(self):
        return self._redis_session

    def start_redis_transaction(self):
        self._redis_session = self._redis_connection.multi_exec()

    async def end_redis_transaction(self):
        self._redis_session and await self._redis_session.execute()



    def get_mongo_collection(self, collection_name) -> AsyncIOMotorCollection:
        return self._mongo_connection[collection_name]
        
    def get_mongo_session(self) -> Optional[AsyncIOMotorClientSession]:
        return self._mongo_session

    async def start_mongo_transaction(self):
        self._mongo_session = await self._mongo_connection.start_session()

    async def end_mongo_transaction(self):
        self._mongo_session and await self._mongo_session.end_session()

