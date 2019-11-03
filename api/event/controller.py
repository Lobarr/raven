import json
import multidict
import pydash
from bson import json_util
from aiohttp import web
from .model import Event
from .schema import event_validator
from api.util import Error, Bson, DB, Validate
from api.circuit_breaker import controller

router = web.RouteTableDef()
table = 'event'


@router.post('/event')
async def post_handler(request: web.Request):
    try:
        ctx = json.loads(await request.text())
        Validate.validate_schema(ctx, event_validator)
        await Event.create(ctx, DB.get(request, table), DB.get(request, controller.table))
        return web.json_response({
            'message': 'Event created',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.get('/event')
async def get_handler(request: web.Request):
    try:
        services = []
        if len(request.rel_url.query.keys()) == 0:
            services = await Event.get_all(DB.get(request, table))
        else:
            if 'id' in request.rel_url.query:
                Validate.validate_object_id(request.rel_url.query.get('id'))
                service = await Event.get_by_id(request.rel_url.query.get('id'), DB.get(request, table))
                if service is not None:
                    services.append(service)
            elif 'circuit_breaker_id' in request.rel_url.query:
                Validate.validate_object_id(
                    request.rel_url.query.get('circuit_breaker_id'))
                services = await Event.get_by_circuit_breaker_id(request.rel_url.query.get('circuit_breaker_id'), DB.get(request, table))
            elif 'target' in request.rel_url.query:
                services = await Event.get_by_target(request.rel_url.query.get('target'), DB.get(request, table))
        return web.json_response({
            'data': DB.format_documents(Bson.to_json(services)),
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.patch('/event')
async def patch_handler(request: web.Request):
    try:
        ctx = json.loads(await request.text())
        event_id = request.rel_url.query['id']
        Validate.validate_object_id(event_id)
        Validate.validate_schema(ctx, event_validator)
        await Event.update(event_id, pydash.omit(ctx, '_id'), DB.get(request, table))
        return web.json_response({
            'message': 'event updated',
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/event')
async def delete_handler(request: web.Request):
    try:
        Validate.validate_object_id(request.rel_url.query.get('id'))
        await Event.remove(request.rel_url.query.get('id'), DB.get(request, table))
        return web.json_response({
            'message': 'Service deleted',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)
