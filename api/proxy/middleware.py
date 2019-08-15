import pydash
import asyncio
import logging
import collections
from multidict import CIMultiDict
from time import time
from aiohttp import web
from api.util import DB, Api, Async, Bson, Error, Bytes
from api.util.tasks import handle_task_async, handle_task_sync
from api.admin import Admin
from api.service import Service, ServiceState, controller as service_controller

@web.middleware
async def proxy(request: web.Request, handler: web.RequestHandler):
  try:
    if pydash.starts_with(request.path_qs, '/raven'):
      return await handler(request)
    matched_services = await Service.get_matched_paths(request.path, DB.get(request, service_controller.table))
    if pydash.is_empty(matched_services):
      raise Exception({
        'message': 'Not found',
        'status_code': 404
      })
    best_matched_service = Service.get_best_service(matched_services)
    if best_matched_service['state'] in [ServiceState.DOWN.name, ServiceState.OFF.name]:
      raise Exception({
        'message': f"Service is currently {best_matched_service['state']}",
        'status_code': 503
      })
    if not pydash.is_empty(best_matched_service['whitelisted_hosts']) and request.remote not in best_matched_service['whitelisted_hosts'] or not pydash.is_empty(best_matched_service['blacklisted_hosts']) and request.remote in best_matched_service['blacklisted_hosts']:
      raise Exception({
        'message': 'Unauthorized',
        'status_code': 401
      })
    request_ctx = {
      'method': request.method,
      'url': best_matched_service['targets'][best_matched_service['cur_target_index']],
      'params': dict(request.rel_url.query),
      'data': await request.text(),
      'cookies':  dict(request.cookies),
      'headers': pydash.omit(dict(request.headers), 'Host'),
    }
    req = await Api.call(**request_ctx)
    # req = handle_task_async.s({
    #   'func': 'Api.call',
    #   'args': [],
    #   'kwargs': request_ctx
    # }).delay().get()
    # logging.info(req['headers'].keys())
    # logging.info(req['headers'])
    handle_task_async.s({
      'func': 'Service.advance_target',
      'args': [str(best_matched_service['_id']), f'mongo:{service_controller.table}'],
      'kwargs': {}
    }).apply_async()
    await Service.advance_target(str(best_matched_service['_id']), DB.get(request, service_controller.table))
    return web.Response(body=Bytes.decode_bytes(req['body_bytes']), status=req['status'], content_type=req['content_type'], headers=CIMultiDict(pydash.omit(req['headers'], 'Content-Type', 'Transfer-Encoding', 'Content-Encoding')))
  except Exception as err:
    return Error.handle(err)
