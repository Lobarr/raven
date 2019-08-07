import pydash
from aiohttp import web
from aioredis import Redis

class DB:
  @staticmethod
  def get(request: web.Request, table: str):
    return request.app['mongo'][table]

  @staticmethod
  def get_redis(request: web.Request) -> Redis:
    return request.app['redis']
  
  @staticmethod
  def format_document(document: object):
    formatted = pydash.omit(document, '_id')
    formatted['_id'] = document['_id']['$oid']
    return formatted
  
  @staticmethod 
  def format_documents(documents: list):
    return list(map(lambda document: DB.format_document(document), documents))
