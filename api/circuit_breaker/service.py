import bson

from pydash import is_empty, has
from enum import Enum
from typing import Optional, List
from aioredis import Redis as AioRedis
from motor.motor_asyncio import AsyncIOMotorCollection

from api.providers import DBProvider
from api.util import DB, Bson
from api.circuit_breaker.schema import CircuitBreakerDTO, CircuitBreakerStatus
from api.service import Service, service_collection_name

collection_name = 'circuit_breaker'

class CircuitBreaker:
    @staticmethod
    async def create(circuit_breaker: CircuitBreakerDTO, db_provider: DBProvider):
        """
        creates a circuit breaker

        @param ctx: (object) context to create
        @param circuit_breaker_db: mongo instance
        @param service_db: mongo instance
        """

        db = db_provider.get_mongo_collection(collection_name)

        if circuit_breaker.service_id:
            await Service.check_exists(
                circuit_breaker.service_id, 
                db_provider.get_mongo_collection(service_collection_name)
            )

        await db.insert_one(circuit_breaker.to_dict(), session=db_provider.get_mongo_session())

    @staticmethod
    async def update(circuit_breaker: CircuitBreakerDTO, db_provider: DBProvider):
        """
        updates circuit breaker

        @param id: (str) id of circuit breaker
        @param ctx: (object) context of update
        @param db: mongo instance
        """

        db = db_provider.get_mongo_collection(collection_name)

        await db.update_one(
            {'_id': bson.ObjectId(circuit_breaker.id)},
            {'$set': circuit_breaker.to_dict()},
            session=db_provider.get_mongo_session()
        )

    @staticmethod
    async def get_by_id(_id: str, db_provider: DBProvider) -> Optional[CircuitBreakerDTO]:
        """
        gets cirbuit breaker by id

        @param id: (str) id of cirbuit breaker
        @param db: mongo instance
        """

        db = db_provider.get_mongo_collection(collection_name)
        circuit_breaker_context = await db.find_one(
            { '_id': bson.ObjectId(_id) }, 
            session=db_provider.get_mongo_session()
        )

        if is_empty(circuit_breaker_context):
            return None

        formatted_circuit_breaker = DB.format_document(Bson.to_json(circuit_breaker_context))

        return CircuitBreaker.make_dto(formatted_circuit_breaker)

    @staticmethod
    async def get_by_service_id(service_id: str, db_provider: DBProvider) -> Optional[CircuitBreakerDTO]:
        """
        gets cirbuit breaker by service id

        @param service_id: (str) service id of cirbuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        circuit_breaker_context = await db.find_one({'service_id': service_id}, session=db_provider.get_mongo_session())

        if is_empty(circuit_breaker_context):
            return None

        formatted_circuit_breaker = DB.format_document(Bson.to_json(circuit_breaker_context))

        return CircuitBreaker.make_dto(formatted_circuit_breaker)

    @staticmethod
    async def get_by_status_code(status_code: int, db_provider: DBProvider) -> List[CircuitBreakerDTO]:
        """
        gets cirbuit breaker by status code

        @param status_code: (int) status code of cirbuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        res = db.find({'status_code': status_code}, session=db_provider.get_mongo_session())
        circuit_breaker_contexts =  await res.to_list(100)

        return [CircuitBreaker.make_dto(circuit_breaker_context) 
                for circuit_breaker_context in circuit_breaker_contexts]

    @staticmethod
    async def get_by_method(method: str, db_provider: DBProvider) -> List[CircuitBreakerDTO]:
        """
        gets cirbuit breaker by method

        @param metod: (str) method of cirbuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        res = db.find({'method': method}, session=db_provider.get_mongo_session())

        circuit_breaker_contexts = await res.to_list(100)

        return [CircuitBreaker.make_dto(circuit_breaker_context) 
                for circuit_breaker_context in circuit_breaker_contexts]

    @staticmethod
    async def get_by_threshold(threshold: float, db_provider: DBProvider) -> List[CircuitBreakerDTO]:
        """
        gets cirbuit breaker by threshold

        @param threshold: (float) threshold of cirbuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        res = db.find({'threshold': threshold}, session=db_provider.get_mongo_session())
        circuit_breaker_contexts = await res.to_list(100)

        return [CircuitBreaker.make_dto(circuit_breaker_context) 
                for circuit_breaker_context in circuit_breaker_contexts]

    @staticmethod
    async def get_all(db_provider: DBProvider) -> List[CircuitBreakerDTO]:
        """
        gets all circuit breakers

        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        res = db.find({}, session=db_provider.get_mongo_session())
        circuit_breaker_contexts = await res.to_list(100)
        
        return [CircuitBreaker.make_dto(circuit_breaker_context) 
                for circuit_breaker_context in circuit_breaker_contexts]

    @staticmethod
    async def remove(_id: str, db_provider: DBProvider):
        """
        removes a cirbuit breaker

        @param id: (str) id of circuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)

        await db.delete_one({'_id': bson.ObjectId(_id)}, session=db_provider.get_mongo_session())

    @staticmethod
    async def check_exists(circuit_breaker_id: str, db_provider: DBProvider):
        """
        checks if circuit breaker exists

        @param circuit_breaker_id: (str) id of circuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        circuit_breaker = await CircuitBreaker.get_by_id(circuit_breaker_id, db_provider)

        if not circuit_breaker:
            raise Exception({
                'message': 'Circuit breaker id provided does not exist',
                'status_code': 400
            })

    @staticmethod
    async def incr_tripped_count(_id: str, db_provider: DBProvider):
        """
        increments tripped count

        @param id: (str) id of circuit breaker
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        await db.update_one(
            { '_id': bson.ObjectId(_id) }, 
            { '$inc': { 'tripped_count': 1 } },
            session=db_provider.get_mongo_session()
        )

    @staticmethod
    def count_key(_id):
        """
        returns count key
        """
        return f'{_id}.count'

    @staticmethod
    def queued_key(_id):
        """
        returns queued key
        """
        return f'{_id}.queued'

    @staticmethod
    async def incr_count(_id: str, db_provider: DBProvider):
        """
        increments count

        @param id: (str) id of circuit breaker
        @param db: redis instance
        """
        db = db_provider.get_redis()

        await db.incr(CircuitBreaker.count_key(_id))

    @staticmethod
    async def get_count(_id: str, db_provider: DBProvider):
        """
        gets count

        @param id: (str) id of circuit breaker
        @param db: redis instance
        """

        db = db_provider.get_redis()

        return await db.get(CircuitBreaker.count_key(_id), encoding='utf-8')

    @staticmethod
    async def set_count(_id: str, count: int, timeout: int, db_provider: DBProvider):
        """
        sets count

        @param id: (str) id of circuit breaker
        @param count: (int) number to set
        @param timeout: (int) redis expire time
        @param db: redis instance
        """
        db = db_provider.get_redis()

        await db.set(CircuitBreaker.count_key(_id), count, expire=timeout)

    @staticmethod
    async def set_queued(_id: str, queued: str, timeout: int, db_provider: DBProvider):
        """
        sets queued (if cooldown has been queued)

        @param id: (str) id of circuit breaker
        @param queued: (str) queue to set
        @param timeout: (int) redis expire time
        @param db: redis instance
        """

        db = db_provider.get_redis()

        await db.set(CircuitBreaker.queued_key(_id), queued, expire=timeout)

    @staticmethod
    async def get_queued(_id: str, db_provider: DBProvider):
        """
        gets queued

        @param id: (str) id of circuit breaker
        @param db: redis instance
        """
        db = db_provider.get_redis()

        return await db.get(CircuitBreaker.queued_key(_id), encoding='utf-8')

    @staticmethod
    def make_dto(ctx: dict, normalize: bool = False) -> CircuitBreakerDTO:
        circuit_breaker = CircuitBreakerDTO()

        if normalize:
            ctx = circuit_breaker.normalize(ctx)

        if has(ctx, '_id') or has(ctx, 'id'):
            circuit_breaker.id = ctx['_id'] if '_id' in ctx else ctx['id']

        if has(ctx, 'status'):
            circuit_breaker.status = CircuitBreakerStatus.ON if ctx['status'] == CircuitBreakerStatus.ON.name else CircuitBreakerStatus.OFF

        if has(ctx, 'service_id'):
            circuit_breaker.service_id = ctx['service_id']

        if has(ctx, 'cooldown'):
            circuit_breaker.cooldown = ctx['cooldown']

        if has(ctx, 'status_codes'):
            circuit_breaker.status_codes = ctx['status_codes']

        if has(ctx, 'methods'):
            circuit_breaker.methods = ctx['methods']

        if has(ctx, 'threshold'):
            circuit_breaker.threshold = ctx['threshold']

        if has(ctx, 'period'):
            circuit_breaker.period = ctx['period']

        if has(ctx, 'tripped_count'):
            circuit_breaker.tripped_count = ctx['tripped_count']

        return circuit_breaker
