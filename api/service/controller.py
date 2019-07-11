import json
from aiohttp import web
from .model import Service

router = web.RouteTableDef()

@router.post('/service')
async def ping(request: web.Request):
  try:
    body = json.loads(await request.text())
    await Service.create(body, request.app['mongo']['service'])
    return web.json_response({
      'message': 'service created',
    })
  except Exception as err:
    return web.json_response({
      'message': err.args,
    }, status=400)
