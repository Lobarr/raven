import pydash

from aiohttp import web
from aioredis import Redis
from api.providers import DBProvider
from motor.motor_asyncio import AsyncIOMotorCollection


class DB:
    @staticmethod
    def get(request: web.Request, collection: str) -> AsyncIOMotorCollection:
        """
        gets a mongo collection instance

        @param request: (Request) aiohttp request instance
        @param collection: (str) name of collection to get
        """
        return request.app['mongo'][collection]

    @staticmethod
    def get_redis(request: web.Request) -> Redis:
        """
        gets redis instance

        @param request: (Request) aiohttp request instance
        """
        return request.app['redis']

    @staticmethod
    def get_provider(request: web.Request) -> DBProvider:
        return request['db_provider']

    @staticmethod
    def format_document(document: dict) -> dict:
        """
        formats mongo document

        @param document: (object) document to format
        """
        if '_id' in document:
            return pydash.merge(
                pydash.omit(document, '_id'),
                {'_id': document['_id']['$oid']}
            )

        return document

    @staticmethod
    def format_documents(documents: list) -> list:
        """
        formats multiple documents

        @param documents: (list) documents to format
        """
        return list(
            map(lambda document: DB.format_document(document), documents))

    @staticmethod
    async def fetch_members(key: str, db: Redis) -> list:
        """
        gets a set from redis

        @param key: (str) id of set to get
        @param db: (Redis) redis instance
        """
        return await db.smembers(key, encoding='utf-8')
