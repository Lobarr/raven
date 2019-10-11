import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Service
from api.util import Error, Bson, DB, Validate
from api.service import service_validator


router = web.RouteTableDef()
table = 'service'

@router.post('/service')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    Validate.validate_schema(ctx, service_validator)
    await Service.create(service_validator.normalized(ctx), DB.get(request, table))
    return web.json_response({
      'message': 'service created',
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/service')
async def get_handler(request: web.Request):
  try:
    if len(request.rel_url.query.keys()) == 0:
      services = await Service.get_all(DB.get(request, table))
      return web.json_response({
        'data': DB.format_documents(Bson.to_json(services)),
        'status_code': 200
      })
    else:
      services = []
      if 'id' in request.rel_url.query:
        Validate.validate_object_id(request.rel_url.query.get('id'))
        service = await Service.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
        if service is not None:
          services.append(service)
      elif 'state' in request.rel_url.query:
        services = await Service.get_by_state(request.rel_url.query.get('state'), DB.get(request, table))
      elif 'secure' in request.rel_url.query:
        services = await Service.get_by_secure(bool(request.rel_url.query.get('secure')), DB.get(request, table))
      return web.json_response({
        'data': DB.format_documents(Bson.to_json(services)),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.patch('/service')
async def patch_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    service_id = request.rel_url.query.get('id')
    Validate.validate_object_id(service_id)
    Validate.validate_schema(ctx, service_validator)
    await Service.update(service_id, ctx, DB.get(request, table))
    return web.json_response({
      'message': 'service updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/service')
async def delete_handler(request: web.Request):
  try:
    Validate.validate_object_id(request.rel_url.query.get('id'))
    await Service.remove(request.rel_url.query.get('id'), DB.get(request, table))
    return web.json_response({
      'message': 'service deleted'
    })
  except Exception as err:
    return Error.handle(err)
