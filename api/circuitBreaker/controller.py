import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import CircuitBreaker
from api.util import Error, Bson, DB


router = web.RouteTableDef()
table = 'circuitBreaker'

@router.post('/circuitBreaker')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    await CircuitBreaker.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'circuitBreaker created',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/circuitBreaker')
async def get_handler(request: web.Request):
  try:
    if len(request.rel_url.query.keys()) == 0:
      circuitBreakers = await CircuitBreaker.get_all(DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(circuitBreakers),
        'status_code': 200
      })
    else:
      circuitBreakers = None
      if 'id' in request.rel_url.query:
        circuitBreakers = await CircuitBreaker.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      elif 'service_id' in request.rel_url.query:
        circuitBreakers = await CircuitBreaker.get_by_service_id(request.rel_url.query.get('service_id'), DB.get(request, table))
      elif 'status_code' in request.rel_url.query:
        circuitBreakers = await CircuitBreaker.get_by_status_code(int(request.rel_url.query.get('status_code')), DB.get(request, table))
      elif 'method' in request.rel_url.query:
        circuitBreakers = await CircuitBreaker.get_by_method(request.rel_url.query.get('method'), DB.get(request, table))
      elif 'path' in request.rel_url.query:
        circuitBreakers = await CircuitBreaker.get_by_path(request.rel_url.query.get('path'), DB.get(request, table))
      elif 'threshold_percent' in request.rel_url.query:
        circuitBreakers = await CircuitBreaker.get_by_threshold_percent(float(request.rel_url.query.get('threshold_percent')), DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(circuitBreakers),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.put('/circuitBreaker')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    circuitBreaker_id = ctx['id']
    await CircuitBreaker.update(circuitBreaker_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'circuitBreaker updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/circuitBreaker')
async def delete_handler(request: web.Request):
  try:
    id = request.rel_url.query.get('id')
    if id is None:
      raise Exception({
        'message': 'Id not provided',
        'status_code': 400
      })
    await CircuitBreaker.remove(id, DB.get(request, table))
    return web.json_response({
      'message': 'circuitBreaker deleted'
    })
  except Exception as err:
    return Error.handle(err)
