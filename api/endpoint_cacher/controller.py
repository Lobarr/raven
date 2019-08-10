import json
import pydash
from aiohttp import web
from .model import EndpointCacher
from .schema import endpoint_cache_schema, endpoint_cache_validator
from api.util import Error, Bson, DB, Validate
from api.service import controller

router = web.RouteTableDef()

@router.get('/endpoint_cache')
async def get_handler(request: web.Request):
  try:
    response = []
    if 'id' in request.rel_url.query:
      _id = request.rel_url.query.get('id')
      Validate.object_id(_id)
      cache = await EndpointCacher.get_by_id(_id, DB.get_redis(request))
      if not pydash.is_empty(cache):
        response.append(cache)
    elif 'service_id' in request.rel_url.query:
      service_id = request.rel_url.query.get('service_id')
      Validate.object_id(service_id)
      response = await EndpointCacher.get_by_service_id(service_id, DB.get_redis(request))
    elif 'endpoint' in request.rel_url.query:
      endpoint = request.rel_url.query.get('endpoint')
      response = await EndpointCacher.get_by_endpoint(endpoint, DB.get_redis(request))
    else:
      response = await EndpointCacher.get_all(DB.get_redis(request))
    return web.json_response({
      'data': response,
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.patch('/endpoint_cache')
async def patch_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    _id = request.rel_url.query.get('id')
    Validate.schema(ctx, endpoint_cache_validator)
    Validate.object_id(_id)
    await EndpointCacher.update(_id, pydash.omit(ctx, 'service_id', 'response_codes'), DB.get_redis(request))
    return web.json_response({
      'message': 'Endpoint cache updated',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
  
@router.patch('/endpoint_cache/response_codes')
async def patch_handler_response_codes(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    _id = request.rel_url.query.get('id')
    action = request.rel_url.query.get('action')
    Validate.object_id(_id)
    Validate.schema(ctx, endpoint_cache_validator)
    if action == 'add':
      await EndpointCacher.add_status_codes(ctx['response_codes'], _id, DB.get_redis(request))
    elif action == 'remove':
      await EndpointCacher.remove_status_codes(ctx['response_codes'], _id, DB.get_redis(request))
    else:
      return web.json_response({
        'message': 'Invalid action provided',
        'status_code': 400,
      }, status=400)
    return web.json_response({
      'message': 'Endpoint cache response codes updated',
      'status_code': 200,
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/endpoint_cache')
async def delete_handler(request: web.Request):
  try:
    _id = request.rel_url.query.get('id')
    Validate.object_id(_id)
    await EndpointCacher.delete(_id, DB.get_redis(request))
    return web.json_response({
      'message': 'Endpoint cache deleted',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

@router.post('/endpoint_cache')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    Validate.schema(ctx, endpoint_cache_validator)
    await EndpointCacher.create(ctx, DB.get_redis(request), DB.get(request, controller.table))
    return web.json_response({
      'message': 'Endpoint cache created', 
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)

