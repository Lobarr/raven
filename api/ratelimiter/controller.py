import json
from aiohttp import web
from bson import json_util
from .model import RateLimiter
from api.util import Error, Bson, DB, Redis
import base64

router = web.RouteTableDef()

@router.get('/rateLimiter/rule')
async def retrieve_rule(request: web.Request):
    try:
        # we want to identify the parameter which is used to identify the records
        if 'path' in request.rel_url.query:
            path = request.rel_url.query['path']
            response = await RateLimiter.get_rules_by_path(path, DB.get_redis(request))
        elif 'statusCode' in request.rel_url.query:
            statusCode = request.rel_url.query['statusCode']
            response = await RateLimiter.get_rules_by_status_code(statusCode, DB.get_redis(request))
        else:
            # fallback to get all if no param passed
            response = await RateLimiter.get_all_rules(DB.get_redis(request))
        results = await Redis.format_response(response)
        return web.json_response({
            'status_code': 200,
            'data': results
        }, status=200)
    except Exception as err:
        return Error.handle(err)
        
@router.post('/rateLimiter/rule')
async def create_rule(request: web.Request):
    try:
        body = json.loads(await request.text())
        data = await RateLimiter.create_rule(body, DB.get_redis(request))
        return web.json_response({
            'message': data,
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
        
@router.put('/rateLimiter/rule')
async def update_rule(request: web.Request):
    try:
        # id is passed thru query params according to spec, data should be passed through request body
        body = json.loads(await request.text())
        id = request.rel_url.query['id']
        await RateLimiter.update_rule(id, body, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter rule updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
        
@router.delete('/rateLimiter/rule')
async def delete_rule(request: web.Request):
    try:
        # id to delete is from query params
        id = request.rel_url.query.get('id')
        if id is None:
            raise Exception({
                'message': 'Id not provided',
                'status_code': 400
            })
        await RateLimiter.delete_rule(id, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter rule deleted',
            'statusCode': 200
        })
    except Exception as err:
        return Error.handle(err)
    
@router.get('/rateLimiter/entry')
async def retrieve_entry(request: web.Request):
    try:
        response = await RateLimiter.get_all_entries(DB.get_redis(request))
        results = await Redis.format_response(response)
        return web.json_response({
            'status_code': 200,
            'data': results
        }, status=200)
    except Exception as err:
        return Error.handle(err)
        
@router.post('/rateLimiter/entry')
async def create_entry(request: web.Request):
    try:
        body = json.loads(await request.text())
        data = await RateLimiter.create_entry(body, DB.get_redis(request))
        return web.json_response({
            'message': data,
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
        
@router.put('/rateLimiter/entry')
async def update_entry(request: web.Request):
    try:
        # id is passed thru query params according to spec, data should be passed through request body
        body = json.loads(await request.text())
        id = request.rel_url.query['id']
        await RateLimiter.update_entry(id, body, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter entry updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
        
@router.delete('/rateLimiter/entry')
async def delete_entry(request: web.Request):
    try:
        # id to delete is from query params
        id = request.rel_url.query.get('id')
        if id is None:
            raise Exception({
                'message': 'Id not provided',
                'status_code': 400
            })
        await RateLimiter.delete_rule(id, DB.get_redis(request))
        return web.json_response({
            'message': 'rate limiter entry deleted',
            'statusCode': 200
        })
    except Exception as err:
        return Error.handle(err)