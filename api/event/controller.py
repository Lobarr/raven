import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Event
from api.util import Error, Bson, DB


router = web.RouteTableDef()
table = 'event'

@router.post('/event')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    await Event.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'event created',
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/event')
async def get_handler(request: web.Request):
  try:
    if len(request._rel_url.query.keys()) == 0:
      services = await Event.get_all(DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(services),
        'status_code': 200
      })
    else:
      services = None
      if 'id' in request._rel_url.query:
        services = await Event.get_by_id(request._rel_url.query.get('id'), DB.get(request, table))
      elif 'circuit_breaker_id' in request._rel_url.query:
        services = await Event.get_by_circuit_breaker_id(request._rel_url.query.get('circuit_breaker_id'), DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(services),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.put('/event')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    event_id = ctx['id']
    await Event.update(event_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'event updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/event')
async def delete_handler(request: web.Request):
  try:
    id = request._rel_url.query.get('id')
    if id is None:
      raise Exception({
        'message': 'Id not provided',
        'status_code': 400
      })
    await Event.remove(id, DB.get(request, table))
    return web.json_response({
      'message': 'service deleted'
    })
  except Exception as err:
    return Error.handle(err)
