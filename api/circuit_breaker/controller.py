import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import CircuitBreaker
from .schema import circuit_breaker_validator
from api.util import Error, Bson, DB, Validate
from api.service import controller


router = web.RouteTableDef()
table = 'circuit_breaker'

@router.post('/circuit_breaker')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    Validate.schema(ctx, circuit_breaker_validator)
    await CircuitBreaker.create(circuit_breaker_validator.normalized(ctx), DB.get(request, table), DB.get(request, controller.table))
    return web.json_response({
      'message': 'Circuit breaker created',
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
      circuit_breakers = []
      if 'id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('id'))
        circuit_breaker = await CircuitBreaker.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
        if circuit_breaker is not None:
          circuit_breakers.append(circuit_breaker)
      elif 'service_id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('service_id'))
        circuit_breakers = await CircuitBreaker.get_by_service_id(request.rel_url.query.get('service_id'), DB.get(request, table))
      elif 'status_code' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_status_code(int(request.rel_url.query.get('status_code')), DB.get(request, table))
      elif 'method' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_method(request.rel_url.query.get('method'), DB.get(request, table))
      elif 'path' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_path(request.rel_url.query.get('path'), DB.get(request, table))
      elif 'threshold' in request.rel_url.query:
        circuit_breakers = await CircuitBreaker.get_by_threshold(float(request.rel_url.query.get('threshold')), DB.get(request, table))
    return web.json_response({
      'data': DB.format_documents(Bson.to_json(circuit_breakers)),
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.put('/circuit_breaker')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    circuit_breaker_id = request.rel_url.query['id']
    Validate.schema(ctx, circuit_breaker_validator)
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
