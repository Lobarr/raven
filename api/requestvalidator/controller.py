import json
from aiohttp import web
from bson import json_util
from .model import RequestValidator
from api.util import Error, Bson, DB

router = web.RouteTableDef()
table = 'requestvalidator'

@router.get('/requestValidation')
async def retrieve(request: web.Request):
    try:
        # we want to identify the parameter which is used to identify the records
        if 'serviceId' in request.rel_url.query:
            service_id = request.rel_url.query['serviceId']
            response = await RequestValidator.get_by_service_id(service_id, DB.get(request, table))
        elif 'method' in request.rel_url.query:
            method = request.rel_url.query['method']
            response = await RequestValidator.get_by_method(method, DB.get(request, table))
        elif 'path' in request.rel_url.query:
            path = request.rel_url.query['path']
            response = await RequestValidator.get_by_path(path, DB.get(request, table))
        else:
            # fallback to get all if no param passed
            response = await RequestValidator.get_all(DB.get(request, table))
        return web.json_response({
            'status_code': 200,
            'data': Bson.to_json(response)
        }, status=200)
    except Exception as err:
        return Error.handle(err)
        
@router.post('/requestValidation')
async def create(request: web.Request):
    try:
        body = json.loads(await request.text())
        await RequestValidator.create(body, DB.get(request, table))
        return web.json_response({
            'message': 'Created request validation',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
        
@router.put('/requestValidation')
async def update(request: web.Request):
    try:
        # id is passed thru query params according to spec, data should be passed through request body
        body = json.loads(await request.text())
        id = request.rel_url.query['id']
        await RequestValidator.update(id, body, DB.get(request, table))
        return web.json_response({
            'message': 'request validation updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
        
@router.delete('/requestValidation')
async def delete(request: web.Request):
    try:
        # id to delete is from query params
        id = request.rel_url.query.get('id')
        if id is None:
            raise Exception({
                'message': 'Id not provided',
                'status_code': 400
            })
        await RequestValidator.delete(id, DB.get(request, table))
        return web.json_response({
            'message': 'request validation deleted',
            'statusCode': 200
        })
    except Exception as err:
        return Error.handle(err)