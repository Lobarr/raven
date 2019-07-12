import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Admin
from api.util import Error, Bson, DB


router = web.RouteTableDef()
table = 'admin'

@router.post('/admin')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    await Admin.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'admin created',
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/admin')
async def get_handler(request: web.Request):
  try:
    if len(request._rel_url.query.keys()) == 0:
      admins = await Admin.get_all(DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(admins),
        'status_code': 200
      })
    else:
      admins = None
      if 'id' in request._rel_url.query:
        admins = await Admin.get_by_id(request._rel_url.query.get('id'), DB.get(request, table))
      elif 'email' in request._rel_url.query:
        admins = await Admin.get_by_email(request._rel_url.query.get('email'), DB.get(request, table))
      elif 'username' in request._rel_url.query:
        admins = await Admin.get_by_username(request._rel_url.query.get('username'), DB.get(request, table))
      return web.json_response({
        'data': Bson.to_json(admins),
        'status_code': 200
      })
  except Exception as err:
    return Error.handle(err)

@router.put('/admin')
async def put_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    admin_id = ctx['id']
    if admin_id is None:
      raise Exception({
        'message': 'id not provided',
        'status_code': 400
      })
    await Admin.update(admin_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'admin updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/admin')
async def delete_handler(request: web.Request):
  try:
    id = request._rel_url.query.get('id')
    if id is None:
      raise Exception({
        'message': 'Id not provided',
        'status_code': 400
      })
    await Admin.remove(id, DB.get(request, table))
    return web.json_response({
      'message': 'admin deleted'
    })
  except Exception as err:
    return Error.handle(err)
