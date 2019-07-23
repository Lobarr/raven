import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Service
from api.util import Error, Bson, DB, Validate


router = web.RouteTableDef()
table = 'service'

@router.post('/service')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    await Service.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'service created',
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/service')
async def get_handler(request: web.Request):
  try:
    if len(request._rel_url.query.keys()) == 0:
      services = await Service.get_all(DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(services),
        'status_code': 200
      })
    else:
      services = None
      if 'id' in request._rel_url.query:
        Validate.object_id(request._rel_url.query.get('id'))
        services = await Service.get_by_id(request._rel_url.query.get('id'), DB.get(request, table))
      elif 'state' in request._rel_url.query:
        services = await Service.get_by_state(request._rel_url.query.get('state'), DB.get(request, table))
      elif 'secure' in request._rel_url.query:
        services = await Service.get_by_secure(bool(request._rel_url.query.get('secure')), DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(services),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.put('/service')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    service_id = ctx['id']
    Validate.object_id(service_id)
    await Service.update(service_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'service updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/service')
async def delete_handler(request: web.Request):
  try:
    id = request._rel_url.query.get('id')
    if id is None:
      raise Exception({
        'message': 'Id not provided',
        'status_code': 400
      })
    Validate.object_id(request._rel_url.query.get('id'))
    await Service.remove(id, DB.get(request, table))
    return web.json_response({
      'message': 'service deleted'
    })
  except Exception as err:
    return Error.handle(err)
