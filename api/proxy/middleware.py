import pydash
import asyncio
from time import time
from aiohttp import web
from api.util import DB, Api
from api.util.tasks import handle_task_async, handle_task_sync
from api.admin import Admin

@web.middleware
async def proxy(request: web.Request, handler: web.RequestHandler):
  if pydash.starts_with(request.path_qs, '/raven'):
    return await handler(request)
  return web.json_response({
    'method': request.method,
    'path': request.path_qs,
    'headers': dict(request.headers),
    'remote': request.remote,
    'query': dict(request.query),
    'cookies': dict(request.cookies),
  })
