import pydash
from aiohttp import web
from aioredis import Redis
from motor.motor_asyncio import AsyncIOMotorCollection

class DB:
  """
  gets a mongo collection instance 

  @param request: (Request) aiohttp request instance
  @param collection: (str) name of collection to get
  """
  @staticmethod
  def get(request: web.Request, collection: str) -> AsyncIOMotorCollection:
    return request.app['mongo'][collection]

  """
  gets redis instance 

  @param request: (Request) aiohttp request instance
  """
  @staticmethod
  def get_redis(request: web.Request) -> Redis:
    return request.app['redis']
  
  """
  formats redis document

  @param document: (object) document to format
  """
  @staticmethod
  def format_document(document: object) -> object:
    formatted = pydash.omit(document, '_id')
    formatted['_id'] = document['_id']['$oid']
    return formatted
  
  """
  formats multiple documents

  @param documents: (list) documents to format
  """
  @staticmethod 
  def format_documents(documents: list) -> list:
    return list(map(lambda document: DB.format_document(document), documents))

  """
  gets a set from redis

  @param key: (str) id of set to get
  @param db: (Redis) redis instance
  """
  @staticmethod
  async def fetch_members(key: str, db: Redis) -> list:
    return await db.smembers(key, encoding='utf-8')
