import json
import multidict
import pydash

from copy import deepcopy
from typing import Optional, Union, List
from bson import json_util
from aiohttp import web
from api.circuit_breaker.service import CircuitBreaker
from api.circuit_breaker.schema import CircuitBreakerDTO
from api.util import Error, Bson, DB, Validate
from api.service import controller


router = web.RouteTableDef()


@router.post('/circuit_breaker')
async def post_handler(request: web.Request):
    try:
        db_provider = deepcopy(DB.get_provider(request))
        ctx = json.loads(await request.text())
        circuit_breaker = CircuitBreaker.make_dto(ctx, normalize=True)

        await db_provider.start_mongo_transaction()
        await CircuitBreaker.create(circuit_breaker, db_provider)
        await db_provider.end_mongo_transaction()

        return web.json_response({
            'message': 'Circuit breaker created',
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.get('/circuit_breaker')
async def get_handler(request: web.Request):
    try:
        db_provider = deepcopy(DB.get_provider(request))
        circuit_breakers: Optional[List[CircuitBreakerDTO]] = None
        circuit_breaker: Optional[CircuitBreakerDTO] = None
        has_prop = len(request.rel_url.query.keys()) > 0

        await db_provider.start_mongo_transaction()

        if not has_prop:

            circuit_breakers = await CircuitBreaker.get_all(db_provider)

        else:

            if 'id' in request.rel_url.query:
                Validate.validate_object_id(request.rel_url.query.get('id'))

                circuit_breaker = await CircuitBreaker.get_by_id(request.rel_url.query.get('id'), db_provider)

            elif 'service_id' in request.rel_url.query:
                Validate.validate_object_id(request.rel_url.query.get('service_id'))

                circuit_breaker = await CircuitBreaker.get_by_service_id(request.rel_url.query.get('service_id'), db_provider)

            elif 'status_code' in request.rel_url.query:
                circuit_breakers = await CircuitBreaker.get_by_status_code(int(request.rel_url.query.get('status_code')), db_provider)

            elif 'method' in request.rel_url.query:
                circuit_breakers = await CircuitBreaker.get_by_method(request.rel_url.query.get('method'), db_provider)

            elif 'threshold' in request.rel_url.query:
                circuit_breakers = await CircuitBreaker.get_by_threshold(float(request.rel_url.query.get('threshold')), db_provider)

        await db_provider.end_mongo_transaction()

        res: Optional[Union[dict, list]] = None

        if circuit_breaker:
            res = circuit_breaker.to_dict()

        if circuit_breakers:
            res = [circuit_breaker.to_dict() for circuit_breaker in circuit_breakers]

        return web.json_response({
            'data': res,
            'status_code': 200
        })
    except Exception as err:
        return Error.handle(err)


@router.patch('/circuit_breaker')
async def patch_handler(request: web.Request):
    try:
        db_provider = deepcopy(DB.get_provider(request))
        ctx = json.loads(await request.text())
        circuit_breaker = CircuitBreaker.make_dto(ctx)
        

        if not circuit_breaker.is_valid():
            raise Exception({
                'message': circuit_breaker.get_validation_errors(),
                'status_code': 400
            })

        await CircuitBreaker.update(circuit_breaker, db_provider)
        
        return web.json_response({
            'message': 'Circuit breaker updated',
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/circuit_breaker')
async def delete_handler(request: web.Request):
    try:
        db_provider = deepcopy(DB.get_provider(request))

        Validate.validate_object_id(request.rel_url.query.get('id'))

        await db_provider.start_mongo_transaction()
        await CircuitBreaker.remove(request.rel_url.query.get('id'), db_provider)
        await db_provider.end_mongo_transaction()

        return web.json_response({
            'message': 'Circuit breaker deleted'
        })
    except Exception as err:
        return Error.handle(err)
