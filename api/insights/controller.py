import json, pydash
import multidict
from bson import json_util
from aiohttp import web
from .model import Insights
from api.util import Error, Bson, DB

router = web.RouteTableDef()
table = 'insights'

def get_db(request: web.Request):
  return request.app['mongo']['insights']

@router.post('/insights')
async def post_handler(request: web.Request):
  try:
    body = json.loads(await request.text())
    await Insights.create(body, DB.get(request, table))
    return web.json_response({
      'message': 'Insight created',
    })
  except Exception as err:
     return Error.handle(err)

@router.get('/insights')
async def get_handler(request: web.Request):
  try:
    if len(request._rel_url.query.keys()) == 0:
      insights = await Insights.get_all(DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(insights),
        'status_code': 200
      })
    else:
      insights = None
      if 'id' in request._rel_url.query:
        insights = await Insights.get_by_id(request._rel_url.query.get('id'), DB.get(request, table))
      elif 'remote_ip' in request._rel_url.query:
        insights = await Insights.get_by_remote_ip(request._rel_url.query.get('remote_ip'), DB.get(request, table))
      elif 'status_code' in request._rel_url.query:
        insights = await Insights.get_by_status_code(bool(request._rel_url.query.get('status_code')))
      elif 'path' in request._rel_url.query:
        insights = await Insights.get_by_path(bool(request._rel_url.query.get('path')))
      elif 'method' in request._rel_url.query:
        insights = await Insights.get_by_method(bool(request._rel_url.query.get('method')))
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
    service_id = ctx['id']
    await Insights.update(service_id, pydash.omit(ctx, 'id'), DB.get(request, 'insights'))
    return web.json_response({
      'message': 'insight updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/insights')
async def delete_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    service_id = ctx['id']
    await Insights.remove(service_id, DB.get(request, 'insights'))
    return web.json_response({
      'message': 'insight deleted',
    })
  except Exception as err:
    return Error.handle(err)