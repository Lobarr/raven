import json
import multidict
import pydash
import copy 

from typing import Optional, List
from bson import json_util
from aiohttp import web
from api.event.service import Event
from api.event.schema import EventDTO
from api.util import Error, Bson, DB, Validate
from api.circuit_breaker import controller

router = web.RouteTableDef()
table = 'event'


@router.post('/event')
async def post_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        ctx = json.loads(await request.text())
        event = Event.make_dto(ctx)

        if not event.is_valid():
            raise Exception({
                'message': event.get_validation_errors(),
                'status_code': 400
            })

        await Event.create(event, db_provider)

        return web.json_response({
            'message': 'Event created',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.get('/event')
async def get_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        has_prop = len(request.rel_url.query.keys()) > 0

        event: Optional[EventDTO] = None
        events: Optional[List[EventDTO]] = None

        await db_provider.start_mongo_transaction()

        if not has_prop:
            events = await Event.get_all(db_provider)

        else:
            
            if 'id' in request.rel_url.query:
                _id = request.rel_url.query.get('id')
                Validate.validate_object_id(_id)
                
                event = await Event.get_by_id(_id, db_provider)

            elif 'circuit_breaker_id' in request.rel_url.query:
                circuit_breaker_id = request.rel_url.query.get('id')
                Validate.validate_object_id(circuit_breaker_id)
                
                events = await Event.get_by_circuit_breaker_id(circuit_breaker_id, db_provider)

            elif 'target' in request.rel_url.query:
                target = request.rel_url.query.get('target')
                events = await Event.get_by_target(target, db_provider)


        await db_provider.end_mongo_transaction()

        if event:                
            return web.json_response({
                'data': event.to_dict() if event else None,
                'status_code': 200
            })
        elif events:
            return web.json_response({
                'data': [_event.to_dict() for _event in events],
                'status_code': 200
            })

        return web.json_response({
            'data': None,
            'status_code': 200
        })
        
    except Exception as err:
        return Error.handle(err)


@router.patch('/event')
async def patch_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        ctx = json.loads(await request.text())
        event = Event.make_dto(ctx)
        event_id = request.rel_url.query.get('id')

        if not event.is_valid():
            raise Exception({
                'message': event.get_validation_errors(),
                'staus_code': 400
            })

        await Event.update(event, db_provider)

        return web.json_response({
            'message': 'Event updated',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/event')
async def delete_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))

        Validate.validate_object_id(request.rel_url.query.get('id'))

        await db_provider.start_mongo_transaction()
        await Event.remove(request.rel_url.query.get('id'), db_provider)
        await db_provider.end_mongo_transaction()

        return web.json_response({
            'message': 'Event deleted',
            'status_code': 200
        })

    except Exception as err:
        return Error.handle(err)
