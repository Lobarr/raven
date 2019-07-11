from aiohttp import web

class DB:
  @staticmethod
  def get(request: web.Request, table: str):
    return request.app['mongo'][table]
