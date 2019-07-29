import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import CircuitBreaker
from .schema import circuit_breaker_validator
from api.util import Error, Bson, DB, Validate


router = web.RouteTableDef()
table = 'circuit_breaker'

@router.post('/circuit_breaker')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    Validate.schema(ctx, circuit_breaker_validator)
    await CircuitBreaker.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'Curcuit breaker created',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/circuit_breaker')
async def get_handler(request: web.Request):
  try:
    circuit_breakers = None
    if len(request.rel_url.query.keys()) == 0:
      circuit_breakers = await CircuitBreaker.get_all(DB.get(request, table))
    else:
      circuit_breakers = None
      if 'id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('id'))
        circuit_breakers = await CircuitBreaker.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      elif 'service_id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('service_id'))
        circuit_breakers = await CircuitBreaker.get_by_service_id(request.rel_url.query.get('service_id'), DB.get(request, table))
      elif 'status_code' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_status_code(int(request.rel_url.query.get('status_code')), DB.get(request, table))
      elif 'method' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_method(request.rel_url.query.get('method'), DB.get(request, table))
      elif 'path' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_path(request.rel_url.query.get('path'), DB.get(request, table))
      elif 'threshold_percent' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_threshold_percent(float(request.rel_url.query.get('threshold_percent')), DB.get(request, table))
    return web.json_response({
      'data': Bson.to_json(circuit_breakers),
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.put('/circuit_breaker')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    circuit_breaker_id = ctx['id']
    Validate.object_id(circuit_breaker_id)
    await CircuitBreaker.update(circuit_breaker_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'Circuit breaker updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/circuit_breaker')
async def delete_handler(request: web.Request):
  try:
    Validate.object_id(request.rel_url.query.get('id'))
    await CircuitBreaker.remove(request.rel_url.query.get('id'), DB.get(request, table))
    return web.json_response({
      'message': 'Circuit breaker deleted'
    })
  except Exception as err:
    return Error.handle(err)
