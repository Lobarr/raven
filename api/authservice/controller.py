import json, pydash
import multidict
from bson import json_util
from aiohttp import web
from .model import Authservice
from api.util import Error, Bson, DB

router = web.RouteTableDef()
table = 'authservice'

@router.post('/authservice')
async def post_handler(request: web.Request):
  try:
    body = json.loads(await request.text())
    await Authservice.create(body, DB.get(request, table))
    return web.json_response({
      'message': 'authservice created',
    })
  except Exception as err:
     return Error.handle(err)

@router.get('/authservice')
async def get_handler(request: web.Request):
  try:
    if len(request.rel_url.query.keys()) == 0:
      authservice = await Authservice.get_all(DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(authservice),
        'status_code': 200
      })
    else:
      authservice = None
      if 'id' in request.rel_url.query:
        authservice = await Authservice.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(authservice),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.put('/authservice')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    service_id = ctx['id']
    await Authservice.update(service_id, pydash.omit(ctx, 'id'), DB.get(request, 'authservice'))
    return web.json_response({
      'message': 'authservice updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/authservice')
async def delete_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    service_id = ctx['id']
    await Authservice.remove(service_id, DB.get(request, 'authservice'))
    return web.json_response({
      'message': 'authservice deleted',
    })
  except Exception as err:
    return Error.handle(err)
