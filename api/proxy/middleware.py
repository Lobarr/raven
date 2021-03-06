import pydash
import time
import json
from datetime import datetime, timedelta
from multidict import CIMultiDict
from time import time
from aiohttp import web

from api.util import DB, Api, Async, Bson, Error, Bytes, Regex, Hasher
from api.util.tasks import queue_async_func
from api.admin import Admin
from api.service import Service, ServiceState, controller as service_controller
from api.circuit_breaker import CircuitBreaker, CircuitBreakerStatus, controller as circuit_breaker_controller
from api.event import Event, controller as event_controller
from api.endpoint_cacher import EndpointCacher
from api.insights import controller as insights_controller
from api.rate_limiter import RateLimiter
from api.request_validator import RequestValidator, controller as request_validator_controller


async def handle_circuit_breaker(breaker: object, service: object, request: web.Request, req: object):
    if req['status'] in breaker['status_codes']:
        breaker_count = await CircuitBreaker.get_count(
            str(breaker['_id']),
            DB.get_redis(request)
        )
    if not breaker_count:
        await CircuitBreaker.set_count(
            str(breaker['_id']),
            0,
            breaker['period'],
            DB.get_redis(request)
        )
    else:
        failures_rate = breaker['tripped_count'] / int(breaker_count)
        if failures_rate >= (1 - breaker['threshold']):
            queued = await CircuitBreaker.get_queued(str(breaker['_id']), DB.get_redis(request))
            if not queued or queued is 'False':
                cooldown_eta = datetime.utcnow(
                ) + timedelta(seconds=breaker['cooldown'])
                queue_async_func.s({'func': 'Service.update',
                                    'args': [str(service['_id']),
                                             {'state': ServiceState.DOWN.name},
                                             f'mongo:{service_controller.table}'],
                                    'kwargs': {}}).apply_async()
                queue_async_func.s({
                    'func': 'CircuitBreaker.set_queued',
                    'args': [str(breaker['_id']), 'True', breaker['cooldown'], 'redis'],
                    'kwargs': {}
                }).apply_async()
                queue_async_func.s({'func': 'Service.update',
                                    'args': [str(service['_id']),
                                             {'state': ServiceState.UP.name},
                                             f'mongo:{service_controller.table}'],
                                    'kwargs': {}}).apply_async(eta=cooldown_eta)
                queue_async_func.s({
                    'func': 'CircuitBreaker.set_queued',
                    'args': [str(breaker['_id']), 'False', breaker['cooldown'], 'redis'],
                    'kwargs': {}
                }).apply_async(eta=cooldown_eta)
                queue_async_func.s({'func': 'CircuitBreaker.update',
                                    'args': [str(breaker['_id']),
                                             {'tripped_count': 0},
                                             f'mongo:{circuit_breaker_controller.table}'],
                                    'kwargs': {}}).apply_async(eta=cooldown_eta)
                events = await Event.get_by_circuit_breaker_id(str(breaker['_id']), DB.get(request, event_controller.table))
                for event in events:
                    queue_async_func.s({
                        'func': 'Event.handle_event',
                        'args': [Bson.to_json(event)],
                        'kwargs': {}
                    }).apply_async()
    await Async.all([
        CircuitBreaker.incr_tripped_count(str(breaker['_id']), DB.get(
            request, circuit_breaker_controller.table)),
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
    if not pydash.is_empty(
            service['whitelisted_hosts']) and remote not in service['whitelisted_hosts'] or not pydash.is_empty(
            service['blacklisted_hosts']) and remote in service['blacklisted_hosts']:
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
        'cookies': dict(request.cookies),
        'headers': pydash.omit(dict(request.headers), 'Host'),
    }
    req = None
    req_cache = None
    req_ctx_hash = None

    if not pydash.is_empty(endpoint_cacher):
        req_ctx_hash = Hasher.hash_sha_256(json.dumps(req_ctx))
        req_cache = await EndpointCacher.get_cache(req_ctx_hash, DB.get_redis(request))

    if pydash.is_empty(req_cache):
        req = await Api.call(**req_ctx)
        if pydash.is_empty(req_ctx_hash):
            req_ctx_hash = Hasher.hash_sha_256(json.dumps(req_ctx))
        not pydash.is_empty(endpoint_cacher) and queue_async_func.s({
            'func': 'EndpointCacher.set_cache',
            'args': [req_ctx_hash, req, int(endpoint_cacher['timeout']), 'redis'],
            'kwargs': {}
        }).apply_async()
    else:
        req = json.loads(req_cache)

    cache_hit = True if not pydash.is_empty(req_cache) else False
    return req, cache_hit


async def handle_insights(request: web.Request, response: object, service_id: str, elapsed_time: int, cache: bool):
    ctx = {
        'method': request.method,
        'service_id': service_id,
        'path': request.path,
        'remote_ip': request.remote,
        'scheme': request.scheme,
        'status_code': response['status'],
        'content_type': response['content_type'],
        'elapsed_time': elapsed_time,
        'cache': cache
    }
    queue_async_func.s({'func': 'Insights.create',
                        'args': [ctx,
                                 f'mongo:{insights_controller.table}',
                                 f'mongo:{service_controller.table}'],
                        'kwargs': {}}).apply_async()


async def handle_rate_limiter(request: web.Request, service_id: str, rule: object):
    if not pydash.is_empty(rule):
        entries = await RateLimiter.get_entry_by_rule_id(rule['_id'], DB.get_redis(request))
        if not pydash.is_empty(entries):
            entry = entries[0]
            if int(entry['count']) >= int(rule['max_requests']):
                raise Exception({
                    'message': rule['message'] or 'Too Many Requests',
                    'status_code': int(rule['status_code']) or 429
                })
            queue_async_func.s({
                'func': 'RateLimiter.increment_entry_count',
                'args': [entry['_id'], 'redis'],
                'kwargs': {}
            }).apply_async()
        else:
            entry = {
                'rule_id': rule['_id'],
                'host': request.remote,
                'count': 1,
                'timeout': int(rule['timeout'])
            }
            queue_async_func.s({
                'func': 'RateLimiter.create_entry',
                'args': [entry, 'redis'],
                'kwargs': {}
            }).apply_async()


async def handle_request_validator(validator: object, ctx: str, method: str):
    if method == validator['method']:
        'schema' in validator and await RequestValidator.validate_schema(ctx, validator['schema'])
        if 'password_field' in validator and 'password_policy' in validator and validator[
                'password_field'] in ctx:
            await RequestValidator.enforce_policy(ctx[validator['password_field']], validator['password_policy'])
            'strength' in validator['password_policy'] and await RequestValidator.enforce_strength(ctx[validator['password_field']], validator['password_policy']['strength'])


@web.middleware
async def proxy(request: web.Request, handler: web.RequestHandler):
    try:
        req_start_time = time()
        if pydash.starts_with(request.path_qs, '/raven'):
            return await handler(request)

        service = Regex.best_match(await Regex.get_matched_paths(request.path, DB.get(request, service_controller.table)))
        await handle_service(service, request.remote)

        rate_limiter_rules = await RateLimiter.get_rule_by_service_id(str(service['_id']), DB.get_redis(request))
        rate_limiter_rule = rate_limiter_rules[0] if rate_limiter_rules else None
        await handle_rate_limiter(request, str(service['_id']), rate_limiter_rule)

        breakers = await CircuitBreaker.get_by_service_id(str(service['_id']), DB.get(request, circuit_breaker_controller.table))
        breaker = breakers[0] if breakers else None

        request_validators = await RequestValidator.get_by_service_id(str(service['_id']), DB.get(request, request_validator_controller.table))
        request_validator = request_validators[0] if request_validators else None

        endpoint_cachers = not pydash.is_empty(service) and await EndpointCacher.get_by_service_id(str(service['_id']), DB.get_redis(request)) or None
        endpoint_cacher = endpoint_cachers[0] if endpoint_cachers else None

        await handle_request_validator(request_validator, json.loads(await request.text()), request.method)
        req, req_cache_hit = await handle_request(request, service, endpoint_cacher)

        checks = []

        if not pydash.is_empty(
                breaker) and breaker['status'] == CircuitBreakerStatus.ON.name:
            if req['status'] in breaker['status_codes']:
                checks.append(handle_circuit_breaker(
                    breaker, service, request, req))
            else:
                await CircuitBreaker.incr_count(str(breaker['_id']), DB.get_redis(request))

        queue_async_func.s({
            'func': 'Service.advance_target',
            'args': [str(service['_id']), f'mongo:{service_controller.table}'],
            'kwargs': {}
        }).apply_async()
        req_finish_time = time()
        req_elapsed_time = req_finish_time - req_start_time
        checks.append(handle_insights(request, req, str(
            service['_id']), req_elapsed_time, req_cache_hit))
        await Async.all(checks)

        return web.Response(
            body=Bytes.decode_bytes(
                req['body_bytes']),
            status=req['status'],
            content_type=req['content_type'],
            headers=CIMultiDict(
                pydash.omit(
                    req['headers'],
                    'Content-Type',
                    'Transfer-Encoding',
                    'Content-Encoding')))
    except Exception as err:
        return Error.handle(err)
