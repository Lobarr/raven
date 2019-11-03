import json
from aiohttp import web
from .model import RateLimiter
from .schema import rate_limit_entry_validator, rate_limit_rule_validator
from api.util import Error, Bson, DB, Validate

router = web.RouteTableDef()


@router.get('/rate_limiter/rule')
async def retrieve_rule(request: web.Request):
    try:
        # we want to identify the parameter which is used to identify the
        # records
        response = []
        if 'status_code' in request.rel_url.query:
            status_code = request.rel_url.query.get('status_code')
            response = await RateLimiter.get_rule_by_status_code(status_code, DB.get_redis(request))
        elif 'service_id' in request.rel_url.query:
            service_id = request.rel_url.query.get('service_id')
            response = await RateLimiter.get_rule_by_service_id(service_id, DB.get_redis(request))
        elif 'id' in request.rel_url.query:
            _id = request.rel_url.query.get('id')
            Validate.validate_object_id(_id)
            rule = await RateLimiter.get_rule_by_id(_id, DB.get_redis(request))
            if rule:
                response.append(rule)
        else:
            # fallback to get all if no param passed
            response = await RateLimiter.get_all_rules(DB.get_redis(request))
        return web.json_response({
            'data': response,
            'status_code': 200
        }, status=200)
    except Exception as err:
        return Error.handle(err)


@router.post('/rate_limiter/rule')
async def create_rule(request: web.Request):
    try:
        ctx = json.loads(await request.text())
        Validate.validate_schema(ctx, rate_limit_rule_validator)
        await RateLimiter.create_rule(ctx, DB.get_redis(request))
        return web.json_response({
            'message': 'Created rate limiter rule',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.patch('/rate_limiter/rule')
async def update_rule(request: web.Request):
    try:
        ctx = json.loads(await request.text())
        _id = request.rel_url.query.get('id')
        Validate.validate_schema(ctx, rate_limit_rule_validator)
        Validate.validate_object_id(_id)
        await RateLimiter.update_rule(_id, ctx, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter rule updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/rate_limiter/rule')
async def delete_rule(request: web.Request):
    try:
        # id to delete is from query params
        _id = request.rel_url.query.get('id')
        Validate.validate_object_id(_id)
        await RateLimiter.delete_rule(_id, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter rule deleted',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.get('/rate_limiter/entry')
async def retrieve_entry(request: web.Request):
    try:
        response = []
        if 'rule_id' in request.rel_url.query:
            rule_id = request.rel_url.query.get('rule_id')
            Validate.validate_object_id(rule_id)
            response = await RateLimiter.get_entry_by_rule_id(rule_id, DB.get_redis(request))
        elif 'host' in request.rel_url.query:
            host = request.rel_url.query.get('host')
            response = await RateLimiter.get_entry_by_host(host, DB.get_redis(request))
        elif 'id' in request.rel_url.query:
            _id = request.rel_url.query.get('id')
            Validate.validate_object_id(_id)
            response = await RateLimiter.get_entry_by_id(_id, DB.get_redis(request))
        else:
            response = await RateLimiter.get_all_entries(DB.get_redis(request))
        return web.json_response({
            'data': response,
            'status_code': 200
        }, status=200)
    except Exception as err:
        return Error.handle(err)


@router.post('/rate_limiter/entry')
async def create_entry(request: web.Request):
    try:
        ctx = json.loads(await request.text())
        Validate.validate_schema(ctx, rate_limit_entry_validator)
        await RateLimiter.create_entry(ctx, DB.get_redis(request))
        return web.json_response({
            'message': "Created rate limiter entry",
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.patch('/rate_limiter/entry')
async def update_entry(request: web.Request):
    try:
        ctx = json.loads(await request.text())
        _id = request.rel_url.query.get('id')
        Validate.validate_schema(ctx, rate_limit_entry_validator)
        Validate.validate_object_id(_id)
        await RateLimiter.update_entry(_id, ctx, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter entry updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/rate_limiter/entry')
async def delete_entry(request: web.Request):
    try:
        # id to delete is from query params
        _id = request.rel_url.query.get('id')
        Validate.validate_object_id(_id)
        await RateLimiter.delete_entry(_id, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter entry deleted',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
