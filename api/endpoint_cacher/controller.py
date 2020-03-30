import json
import pydash
import copy

from typing import Optional, List, Any
from aiohttp import web
from api.endpoint_cacher.service import EndpointCacher
from api.endpoint_cacher.schema import EndpointCacherDTO
from api.util import Error, Bson, DB, Validate

router = web.RouteTableDef()

@router.get('/endpoint_cache')
async def get_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        has_prop = len(request.rel_url.query.keys()) > 0
        endpoint_cachers: Optional[List[EndpointCacherDTO]] = None
        endpoint_cacher: Optional[EndpointCacherDTO] = None
        
        if not has_prop:
            endpoint_cachers = await EndpointCacher.get_all(db_provider)

            return web.json_response({
                'data': [endpoint_cacher.to_dict() for endpoint_cacher in endpoint_cachers],
                'status_code': 200
            })
        
        else:

            if 'id' in request.rel_url.query:
                endpoint_cacher_id = request.rel_url.query.get('id')
                Validate.validate_object_id(endpoint_cacher_id)

                endpoint_cacher = await EndpointCacher.get_by_id(endpoint_cacher_id, db_provider)

            elif 'service_id' in request.rel_url.query:
                service_id = request.rel_url.query.get('service_id')
                Validate.validate_object_id(service_id)

                endpoint_cachers = await EndpointCacher.get_by_service_id(service_id, db_provider)

            response: Any = None

            if endpoint_cachers:
                response = [endpoint_cacher.to_dict() for endpoint_cacher in endpoint_cachers]

            if endpoint_cacher:
                response = endpoint_cacher.to_dict()

            return web.json_response({
                'data': response,
                'status_code': 200
            })

    except Exception as err:
        return Error.handle(err)


@router.patch('/endpoint_cache')
async def patch_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        endpoint_cacher_context = json.loads(await request.text())
        endpoint_cacher = EndpointCacher.make_dto(endpoint_cacher_context)

        Validate.validate_object_id(endpoint_cacher.id)

        if not endpoint_cacher.is_valid():
            raise Exception({
                'message': endpoint_cacher.get_validation_errors(),
                'status_code': 400
            })
        
        await EndpointCacher.update(endpoint_cacher, db_provider)

        return web.json_response({
            'message': 'Endpoint cache updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.patch('/endpoint_cache/{id}/response_codes')
async def patch_handler_response_codes(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        ctx = json.loads(await request.text())
        endpoint_cacher_id = request.match_info['id']
        action = request.rel_url.query.get('action')

        Validate.validate_object_id(endpoint_cacher_id)

        if action == 'add':
            await EndpointCacher.add_status_codes(ctx['response_codes'], endpoint_cacher_id, DB.get_redis(request))

        elif action == 'remove':
            await EndpointCacher.remove_status_codes(ctx['response_codes'], endpoint_cacher_id, DB.get_redis(request))

        else:
            return web.json_response({
                'message': 'Invalid action provided',
                'status_code': 400,
            }, status=400)

        return web.json_response({
            'message': 'Endpoint cache response codes updated',
            'status_code': 200,
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/endpoint_cache')
async def delete_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        endpoint_cacher_id = request.rel_url.query.get('id')

        Validate.validate_object_id(endpoint_cacher_id)
        
        await EndpointCacher.delete(endpoint_cacher_id, db_provider)

        return web.json_response({
            'message': 'Endpoint cache deleted',
            'status_code': 200
        })

    except Exception as err:
        return Error.handle(err)


@router.post('/endpoint_cache')
async def post_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        endpoint_cacher_context = json.loads(await request.text())
        endpoint_cacher = EndpointCacher.make_dto(endpoint_cacher_context)

        if not endpoint_cacher.is_valid():
            raise Exception({
                'message': endpoint_cacher.get_validation_errors(),
                'status_code': 400
            })
        
        await EndpointCacher.create(endpoint_cacher, db_provider)

        return web.json_response({
            'message': 'Endpoint cache created',
            'status_code': 200
        })

    except Exception as err:
        return Error.handle(err)
