import json
import pydash
from aiohttp import web
from bson import json_util
from .model import RequestValidator
from .schema import request_validator
from api.util import Error, Bson, DB, Validate
from api.service import Service, controller

router = web.RouteTableDef()
table = 'request_validator'

@router.get('/request_validator')
async def get_handler(request: web.Request):
  try:
    response = []
    if 'service_id' in request.rel_url.query:
      Validate.validate_object_id(request.rel_url.query['service_id'])
      service_id = request.rel_url.query['service_id']
      response = await RequestValidator.get_by_service_id(service_id, DB.get(request, table))
    elif 'id' in request.rel_url.query:
      Validate.validate_object_id(request.rel_url.query.get('id'))
      req_validator = await RequestValidator.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      if req_validator is not None:
        response.append(req_validator)
    elif 'method' in request.rel_url.query:
      method = request.rel_url.query['method']
      response = await RequestValidator.get_by_method(method, DB.get(request, table))
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
    Validate.validate_schema(body, request_validator)
    await RequestValidator.create(request_validator.normalized(body), DB.get(request, table), DB.get(request, controller.table))
    return web.json_response({
        'message': 'Request validator created',
        'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
      
@router.patch('/request_validator')
async def update_handler(request: web.Request):
  try:
    id = request.rel_url.query['id']
    body = json.loads(await request.text())
    Validate.validate_object_id(id)
    Validate.validate_schema(body, request_validator)
    await RequestValidator.update(id, body, DB.get(request, table))
    return web.json_response({
      'message': 'request validator updated',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
        
@router.delete('/request_validator')
async def delete_handler(request: web.Request):
  try:
    id = request.rel_url.query.get('id')
    Validate.validate_object_id(id)
    await RequestValidator.delete(id, DB.get(request, table))
    return web.json_response({
      'message': 'request validator deleted',
      'statusCode': 200
    })
  except Exception as err:
    return Error.handle(err)
