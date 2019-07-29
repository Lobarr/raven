import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Event
from .schema import event_validator
from api.util import Error, Bson, DB, Validate

router = web.RouteTableDef()
table = 'event'

@router.post('/event')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    Validate.schema(ctx, event_validator)
    await Event.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'Event created',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/event')
async def get_handler(request: web.Request):
  try:
    services = None
    if len(request.rel_url.query.keys()) == 0:
      services = await Event.get_all(DB.get(request, table))
    else:
      if 'id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('id'))
        services = await Event.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      elif 'circuit_breaker_id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('circuit_breaker_id'))
        services = await Event.get_by_circuit_breaker_id(request.rel_url.query.get('circuit_breaker_id'), DB.get(request, table))
      elif 'target' in request.rel_url.query:
        services = await Event.get_by_target(request._rel_url.query.get('target'), DB.get(request, table))
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
    Validate.object_id(event_id)
    await Event.update(event_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'event updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/event')
async def delete_handler(request: web.Request):
  try:
    Validate.object_id(request.rel_url.query.get('id'))
    await Event.remove(request.rel_url.query.get('id'), DB.get(request, table))
    return web.json_response({
      'message': 'Service deleted',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
