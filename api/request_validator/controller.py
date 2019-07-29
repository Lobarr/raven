import json
import pydash
from aiohttp import web
from bson import json_util
from .model import RequestValidator
from .schema import request_validator
from api.util import Error, Bson, DB, Validate

router = web.RouteTableDef()
table = 'request_validator'

@router.get('/request_validator')
async def get_handler(request: web.Request):
  try:
    if 'service_id' in request.rel_url.query:
      Validate.object_id(request.rel_url.query['service_id'])
      service_id = request.rel_url.query['service_id']
      response = await RequestValidator.get_by_service_id(service_id, DB.get(request, table))
    elif 'method' in request.rel_url.query:
      method = request.rel_url.query['method']
      response = await RequestValidator.get_by_method(method, DB.get(request, table))
    elif 'endpoint' in request.rel_url.query:
      path = request.rel_url.query['endpoint']
      response = await RequestValidator.get_by_path(path, DB.get(request, table))
    else:
      response = await RequestValidator.get_all(DB.get(request, table))
    return web.json_response({
      'status_code': 200,
      'data': Bson.to_json(response)
    }, status=200)
  except Exception as err:
    return Error.handle(err)

@router.post('/request_validator')
async def create_handler(request: web.Request):
  try:
    body = json.loads(await request.text())
    Validate.schema(body, request_validator)
    await RequestValidator.create(body, DB.get(request, table))
    return web.json_response({
        'message': 'Created request validation',
        'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
      
@router.put('/request_validator')
async def update_handler(request: web.Request):
  try:
    body = json.loads(await request.text())
    id = request.rel_url.query['id']
    await RequestValidator.update(id, body, DB.get(request, table))
    return web.json_response({
      'message': 'request validation updated',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
        
@router.delete('/request_validator')
async def delete(request: web.Request):
  try:
    id = request.rel_url.query.get('id')
    if id is None:
        raise Exception({
          'message': 'Id not provided',
          'status_code': 400
        })
    await RequestValidator.delete(id, DB.get(request, table))
    return web.json_response({
      'message': 'request validation deleted',
      'statusCode': 200
    })
  except Exception as err:
    return Error.handle(err)