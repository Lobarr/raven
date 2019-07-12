from aiohttp import web

class DB:
  @staticmethod
  def get(request: web.Request, table: str):
    return request.app['mongo'][table]

  @staticmethod
  def get_redis(request: web.Request):
    return request.app['redis']