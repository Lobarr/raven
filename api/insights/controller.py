import json, pydash
import multidict
from bson import json_util
from aiohttp import web
from .schema import insights_validator
from .model import Insights
from api.util import Error, Bson, DB, Validate

router = web.RouteTableDef()
table = 'insights'

@router.post('/insights')
async def post_handler(request: web.Request):
  try:
    body = json.loads(await request.text())
    Validate.schema(body, insights_validator)
    await Insights.create(body, DB.get(request, table))
    return web.json_response({
      'message': 'Insight created',
      'status_code': 200
    })
  except Exception as err:
     return Error.handle(err)

@router.get('/insights')
async def get_handler(request: web.Request):
  try:
    if len(request.rel_url.query.keys()) == 0:
      insights = await Insights.get_all(DB.get(request, table))
    else:
      insights = None
      if 'id' in request.rel_url.query:
        insights = await Insights.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      elif 'remote_ip' in request.rel_url.query:
        insights = await Insights.get_by_remote_ip(request.rel_url.query.get('remote_ip'), DB.get(request, table))
      elif 'status_code' in request.rel_url.query:
        insights = await Insights.get_by_status_code(request.rel_url.query.get('status_code'), DB.get(request, table))
      elif 'path' in request.rel_url.query:
        insights = await Insights.get_by_path(request.rel_url.query.get('path'), DB.get(request, table))
      elif 'method' in request.rel_url.query:
        insights = await Insights.get_by_method(request.rel_url.query.get('method'), DB.get(request, table))
      elif 'service_id' in request.rel_url.query:
        insights = await Insights.get_by_service_id(request.rel_url.query.get('service_id'), DB.get(request, table))
      elif 'scheme' in request.rel_url.query:
        insights = await Insights.get_by_scheme(request.rel_url.query.get('scheme'), DB.get(request, table))
    return web.json_response({
        'data': Bson.to_json(insights),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.put('/insights')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    service_id = request.rel_url.query['id']
    Validate.object_id(service_id)
    Validate.schema(ctx, insights_validator)
    await Insights.update(service_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'insight updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/insights')
async def delete_handler(request: web.Request):
  try:
    service_id = request.rel_url.query.get('id')
    Validate.object_id(service_id)
    await Insights.remove(service_id, DB.get(request, table))
    return web.json_response({
      'message': 'insight deleted',
      'status_code': 200
    })
  except Exception as err:
    return Error.handle(err)
