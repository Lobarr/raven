import pydash
import asyncio
import logging
import time
import re
import json
from datetime import datetime, timedelta
from multidict import CIMultiDict
from time import time
from aiohttp import web

from api.util import DB, Api, Async, Bson, Error, Bytes, Regex, Hasher
from api.util.tasks import handle_task_async, handle_task_sync
from api.admin import Admin
from api.service import Service, ServiceState, controller as service_controller
from api.circuit_breaker import CircuitBreaker, CircuitBreakerStatus, controller as circuit_breaker_controller
from api.event import Event, controller as event_controller
from api.endpoint_cacher import EndpointCacher

async def handle_circuit_breaker(breaker: object, service: object, request: web.Request, req: object):
  if req['status'] in breaker['status_codes']:
    breaker_count = await CircuitBreaker.get_count(str(breaker['_id']), DB.get_redis(request))
  if not breaker_count:
      await CircuitBreaker.set_count(str(breaker['_id']), 0, breaker['period'], DB.get_redis(request))
  else:
    failures_rate = breaker['tripped_count'] / int(breaker_count)
    if failures_rate >= (1 - breaker['threshold']):
      queued = await CircuitBreaker.get_queued(str(breaker['_id']), DB.get_redis(request))
      if not queued or queued is 'False':
        cooldown_eta = datetime.utcnow() + timedelta(seconds=breaker['cooldown'])
        handle_task_async.s({
          'func': 'Service.update',
          'args': [str(service['_id']), {'state': ServiceState.DOWN.name}, f'mongo:{service_controller.table}'],
          'kwargs': {}
        }).apply_async()
        handle_task_async.s({
          'func': 'CircuitBreaker.set_queued',
          'args': [str(breaker['_id']), 'True', breaker['cooldown'], 'redis'],
          'kwargs': {}
        }).apply_async()
        handle_task_async.s({
          'func': 'Service.update',
          'args': [str(service['_id']), {'state': ServiceState.UP.name}, f'mongo:{service_controller.table}'],
          'kwargs': {}
        }).apply_async(eta=cooldown_eta)
        handle_task_async.s({
          'func': 'CircuitBreaker.set_queued',
          'args': [str(breaker['_id']), 'False', breaker['cooldown'], 'redis'],
          'kwargs': {}
        }).apply_async(eta=cooldown_eta)
        handle_task_async.s({
          'func': 'CircuitBreaker.update',
          'args': [str(breaker['_id']), {'tripped_count': 0}, f'mongo:{circuit_breaker_controller.table}'],
          'kwargs': {}
        }).apply_async(eta=cooldown_eta)
        events = await Event.get_by_circuit_breaker_id(str(breaker['_id']), DB.get(request, event_controller.table))
        for event in events:
          handle_task_async.s({
            'func': 'Event.handle_event',
            'args': [Bson.to_json(event)],
            'kwargs': {}
          }).apply_async()
  await Async.all([
    CircuitBreaker.incr_tripped_count(str(breaker['_id']), DB.get(request, circuit_breaker_controller.table)),
    CircuitBreaker.incr_count(str(breaker['_id']), DB.get_redis(request))
  ])

async def handle_service(service: object, remote: str): 
  if pydash.is_empty(service):
    raise Exception({
      'message': 'Not found',
      'status_code': 404
    })
  if service['state'] in [ServiceState.DOWN.name, ServiceState.OFF.name]:
    raise Exception({
      'message': f"Service is currently {service['state']}",
      'status_code': 503
    })
  if not pydash.is_empty(service['whitelisted_hosts']) and remote not in service['whitelisted_hosts'] or not pydash.is_empty(service['blacklisted_hosts']) and remote in service['blacklisted_hosts']:
    raise Exception({
      'message': 'Unauthorized',
      'status_code': 401
    })

async def handle_request(request: web.Request, service: object, endpoint_cacher: object):
  req_ctx = {
    'method': request.method,
    'url': service['targets'][service['cur_target_index']],
    'params': dict(request.rel_url.query),
    'data': await request.text(),
    'cookies':  dict(request.cookies),
    'headers': pydash.omit(dict(request.headers), 'Host'),
  }
  req = None
  req_cache = None
  req_ctx_hash = None
  
  if not pydash.is_empty(endpoint_cacher):
    req_ctx_hash = Hasher.hash_sha_256(json.dumps(req_ctx))
    req_cache = await EndpointCacher.get_cache(req_ctx_hash, DB.get_redis(request))

  if pydash.is_empty(req_cache):
    logging.info('making api call')
    req = await Api.call(**req_ctx)
    if pydash.is_empty(req_ctx_hash):
       req_ctx_hash = Hasher.hash_sha_256(json.dumps(req_ctx))
    not pydash.is_empty(endpoint_cacher) and handle_task_async.s({
        'func': 'EndpointCacher.set_cache',
        'args': [req_ctx_hash, req, int(endpoint_cacher['timeout']), 'redis'],
        'kwargs': {}
      }).apply_async()
  else:
    req = json.loads(req_cache)
  
  return req

@web.middleware
async def proxy(request: web.Request, handler: web.RequestHandler):
  try:
    if pydash.starts_with(request.path_qs, '/raven'):
      return await handler(request)

    prereq = await Async.all([
      Regex.get_matched_paths(request.path, DB.get(request, service_controller.table)),
    ])
    service = Regex.best_match(prereq[0])
    await handle_service(service, request.remote)
    breakers = await CircuitBreaker.get_by_service_id(str(service['_id']), DB.get(request, circuit_breaker_controller.table))
    breaker = breakers[0] if len(breakers) > 0 else None
    endpoint_cachers = not pydash.is_empty(service) and await EndpointCacher.get_by_service_id(str(service['_id']), DB.get_redis(request)) or None
    endpoint_cacher = endpoint_cachers[0] if len(endpoint_cachers) > 0 else None
    req = await handle_request(request, service, endpoint_cacher)
    checks = []

    if not pydash.is_empty(breaker) and breaker['status'] == CircuitBreakerStatus.ON.name:
      if req['status'] in breaker['status_codes']:
        checks.append(handle_circuit_breaker(breaker, service, request, req))
      else:
        await CircuitBreaker.incr_count(str(breaker['_id']), DB.get_redis(request))
    await Async.all(checks)
    handle_task_async.s({
      'func': 'Service.advance_target',
      'args': [str(service['_id']), f'mongo:{service_controller.table}'],
      'kwargs': {}
    }).apply_async()

    return web.Response(body=Bytes.decode_bytes(req['body_bytes']), status=req['status'], content_type=req['content_type'], headers=CIMultiDict(pydash.omit(req['headers'], 'Content-Type', 'Transfer-Encoding', 'Content-Encoding')))
  except Exception as err:
    return Error.handle(err)
