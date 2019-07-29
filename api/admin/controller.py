import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Admin
from .schema import admin_validator
from api.util import Error, Bson, DB, Validate

router = web.RouteTableDef()
table = 'admin'

@router.post('/admin')
async def post_handler(request: web.Request):
  try:
    ctx = json.loads(await request.text())
    Validate.schema(ctx, admin_validator)
    await Admin.create(ctx, DB.get(request, table))
    return web.json_response({
      'message': 'Ammin created',
    })
  except Exception as err:
    return Error.handle(err)

@router.get('/admin')
async def get_handler(request: web.Request):
  try:
    admins = None
    if len(request.rel_url.query.keys()) == 0:
      admins = await Admin.get_all(DB.get(request, table))
    else:
      admins = None
      if 'id' in request.rel_url.query:
        Validate.object_id(request.rel_url.query.get('id'))
        admins = await Admin.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
      elif 'email' in request.rel_url.query:
        admins = await Admin.get_by_email(request.rel_url.query.get('email'), DB.get(request, table))
      elif 'username' in request.rel_url.query:
        admins = await Admin.get_by_username(request.rel_url.query.get('username'), DB.get(request, table))
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
    Validate.object_id(admin_id)
    await Admin.update(admin_id, pydash.omit(ctx, 'id'), DB.get(request, table))
    return web.json_response({
      'message': 'Admin updated',
    })
  except Exception as err:
    return Error.handle(err)

@router.delete('/admin')
async def delete_handler(request: web.Request):
  try:
    Validate.object_id(request.rel_url.query.get('id'))
    await Admin.remove(request.rel_url.query.get('id'), DB.get(request, table))
    return web.json_response({
      'message': 'Admin deleted'
    })
  except Exception as err:
    return Error.handle(err)
