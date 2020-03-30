import bson
import asyncio
import json

from cerberus import Validator
from pydash import merge, is_empty, omit, has
from typing import List
from api.endpoint_cacher.schema import EndpointCacherDTO
from api.rate_limiter.schema import rate_limit_rule_schema, rate_limit_rule_validator, rate_limit_entry_schema, rate_limit_entry_validator
from api.util import Bson, DB, Async
from api.providers import DBProvider
from api.service import Service

endpoint_cacher_set = 'endpoint_cacher_set'
endpoint_cache_service_id_index = 'endpoint_cache_service_id'

"""

The purpose of the indexes is to speed up the process of searching specific fields in a redis stored EndpointCacher object. 
Since we cannot have complex queries in redis, a redis hashmap is used as an index to store highly used fields.
This is achieved by mapping the id of the EndpointCacher to the field's value. 
endpoint_cacher.id --> *field's value*

"""

class EndpointCacher:


    @staticmethod
    async def _set_indexes(endpoint_cacher: EndpointCacherDTO, db_provider: DBProvider):
        #TODO: fix up all comments 

        """
        sets secondary indexes

        @param ctx: indexes to set
        @param db: redis instance
        """

        db = db_provider.get_redis()
        coroutines = []
        indexes = [
            ('service_id', endpoint_cache_service_id_index)
        ]
        
        for index in indexes:
            field = index[0]
            field_redis_key = index[1]
            
            if endpoint_cacher.is_field_none(field):
                coroutines.append(
                    db.hset(field_redis_key, endpoint_cacher.id, endpoint_cacher.get_field(field))
                )

        await Async.all(coroutines)

    @staticmethod
    async def _clear_indexes(_id: str, db: DBProvider):
        """
        clears secondary indexes for specified id

        @param id: id of entity
        @param db: redis instance
        """
        coroutines = []

        for index in [endpoint_cache_service_id_index]:
            coroutines.append(db.hdel(index, _id))

        await Async.all(coroutines)

    @staticmethod
    async def _search_indexes(index: str, search: str, db_provider: DBProvider) -> List[str]:
        """
        searches secondary indexes

        @param index: (str) index to search
        @param serach: (str) serach value
        @param db: redis instance
        """
        db = db_provider.get_redis()
        endpoint_cacher_ids = []
        cursor = b'0'

        while cursor:
            cursor, index_entries = await db.hscan(index, cursor)

            for index_entry in index_entries:
                endpoint_cacher_id = index_entry[0].decode('utf-8')
                field_value = index_entry[1].decode('utf-8')

                if field_value == search:
                    endpoint_cacher_ids.append(endpoint_cacher_id)

        return endpoint_cacher_ids

    @staticmethod
    async def create(endpoint_cacher: EndpointCacherDTO, db_provider: DBProvider):
        """
        creates an endpoint cache

        @param ctx: (object) data to be inserted
        @param db: (object) db connection
        @param service_db: (object) db connection
        """

        db = db_provider.get_redis()
        endpoint_cacher.id = str(bson.ObjectId())

        if endpoint_cacher.service_id:
            await Service.check_exists(endpoint_cacher.service_id, db_provider)

        if endpoint_cacher.response_codes:
            response_codes_id = str(bson.ObjectId())

            for response_code in endpoint_cacher.response_codes:
                await db.sadd(response_codes_id, response_code)

            # replace response_codes with response_codes_id because a set is used to hold the response codes
            endpoint_cacher_context = merge(
                omit(endpoint_cacher.to_dict(), 'response_codes'), 
                { 'response_codes_id': response_codes_id }
            )

        await asyncio.gather(
            EndpointCacher._set_indexes(endpoint_cacher, db_provider),
            db.hmset_dict(endpoint_cacher.id, endpoint_cacher_context),
            db.sadd(endpoint_cacher_set, endpoint_cacher.id),
        )

    @staticmethod
    async def update(endpoint_cacher: EndpointCacherDTO, db_provider: DBProvider):
        """
        updates an endpoint cache.

        @param id: (str) id of endpoint cache to update
        @param ctx: (object) data to use for update
        @param db: (object) db connection
        """
        db = db_provider.get_redis()
        endpoint_cacher_context = None
        response_codes_id = ''


        if endpoint_cacher.service_id:
            await EndpointCacher._set_indexes(endpoint_cacher, db_provider)

        if endpoint_cacher.response_codes:
            endpoint_cacher_context = await db.hgetall(endpoint_cacher.id, encoding='utf-8')

            if 'response_codes_id' in endpoint_cacher_context:
                response_codes_id = endpoint_cacher_context['response_codes_id']
                await db.delete(response_codes_id)
            else:
                response_codes_id = str(bson.ObjectId())
                endpoint_cacher_context['response_codes_id'] = response_codes_id
            

            for response_code in endpoint_cacher.response_codes:
                await db.sadd(response_codes_id, response_code)

        await db.hmset_dict(
            endpoint_cacher.id,
            merge(
                omit(endpoint_cacher.to_dict(), 'response_codes'),
                { 'response_codes_id': response_codes_id }
            )
        )
    
    @staticmethod
    async def delete(_id: str, db_provider: DBProvider):
        """
        deletes a endpoint cache rule.

        @param id: (string) id of endpoint cache to delete
        @param db: (object) db connection
        """
        db = db_provider.get_redis()
        
        await asyncio.gather(
            db.delete(_id),
            EndpointCacher._clear_indexes(_id, db_provider),
            db.srem(endpoint_cacher_set, _id),
        )

    @staticmethod
    async def get_by_id(_id: str, db_provider: DBProvider) -> EndpointCacherDTO:
        """
        gets endpoint cache by id

        @param id: (str) id of endpoint cache
        @param db: db connection
        """
        db = db_provider.get_redis()
        endpoint_cacher_context = await db.hgetall(_id, encoding='utf-8')
        response_codes = None

        if 'response_codes_id' in endpoint_cacher_context:
            response_codes_id = endpoint_cacher_context['response_codes_id']
            response_codes = await db.smembers(response_codes_id, encoding='utf-8')
        
        if not is_empty(response_codes):
            endpoint_cacher_context = merge(
                endpoint_cacher_context, 
                { 'response_codes': response_codes }
            )

        return EndpointCacher.make_dto(omit(endpoint_cacher_context, 'response_codes_id'))

    @staticmethod
    async def get_by_service_id(service_id: str, db_provider: DBProvider) -> List[EndpointCacherDTO]:
        """
        gets endpoint cache by service id

        @param service_id: (str) service id of endpoint cache
        @param db: db connection
        """
        db = db_provider.get_redis()
        endpoint_cachers: List[EndpointCacherDTO] = []
        endpoint_cacher_keys = await EndpointCacher._search_indexes(endpoint_cache_service_id_index, service_id, db_provider)

        for endpoint_cache_key in endpoint_cacher_keys:
            endpoint_cacher_context = await db.hgetall(endpoint_cache_key, encoding='utf-8')
            response_codes = None

            if 'response_codes_id' in endpoint_cacher_context:
                response_codes_id = endpoint_cacher_context['response_codes_id']
                response_codes = await db.smembers(response_codes_id, encoding='utf-8')

            endpoint_cacher = EndpointCacher.make_dto(
                omit(endpoint_cacher_context, 'response_codes_id')
            )

            if not is_empty(response_codes):
                endpoint_cacher.response_codes = response_codes

            endpoint_cachers.append(endpoint_cacher)

        return endpoint_cachers

    @staticmethod
    async def get_all(db_provider: DBProvider) -> List[EndpointCacherDTO]:
        """
        gets all endpoint caches

        @param db: db connection
        """
        db = db_provider.get_redis()
        endpoint_cachers = []
        endpoint_cacher_keys = await DB.fetch_members(endpoint_cacher_set, db)

        for endpoint_cacher_key in endpoint_cacher_keys:
            endpoint_cacher_context = await db.hgetall(endpoint_cacher_key, encoding='utf-8')
            response_codes = None

            if 'response_codes_id' in endpoint_cacher_context:
                response_codes_id = endpoint_cacher_context['response_codes_id']
                response_codes = await db.smembers(response_codes_id, encoding='utf-8')

            endpoint_cacher = EndpointCacher.make_dto(
                omit(endpoint_cacher_context, 'response_codes_id')
            )

            if not is_empty(response_codes):
                endpoint_cacher.response_codes = response_codes

            endpoint_cachers.append(endpoint_cacher)

        return endpoint_cachers

    @staticmethod
    async def add_status_codes(status_codes: list, _id: str, db_provider: DBProvider):
        """
        adds status codes to endpoint cache

        @param status_codes: (list) status codes to add
        @param id: (str) id of endpoint cache
        @param db: db connection
        """
        db = db_provider.get_redis()
        endpoint_cacher = await db.hgetall(_id, encoding='utf-8')

        if not has(endpoint_cacher, 'response_codes_id'):
            raise Exception({
                'message': f'Unable to update cache {_id}',
                'status_code': 400
            })

        for status_code in status_codes:
            await db.sadd(endpoint_cacher['response_codes_id'], status_code)

    @staticmethod
    async def remove_status_codes(status_codes: list, _id: str, db_provider: DBProvider):
        """
        removes status codes to endpoint cache

        @param status_codes: (list) status codes to remove
        @param id: (str) id of endpoint cache
        @param db: db connection
        """
        db = db_provider.get_redis()
        endpoint_cache = await db.hgetall(_id, encoding='utf-8')

        if not has(endpoint_cache, 'response_codes_id'):
            raise Exception({
                'message': f'Unable to update cache {_id}',
                'status_code': 400
            })

        for status_code in status_codes:
            await db.srem(endpoint_cache['response_codes_id'], status_code)

    @staticmethod
    async def set_cache(_hash: str, ctx: dict, timeout: int, db_provider: DBProvider):
        """
        sets cache

        @param _hash: (str) hash of request
        @param ctx: (object) body of response
        """

        db = db_provider.get_redis()
        omit_keys = list(filter(lambda key: ctx[key] is None, ctx.keys()))

        await db.set(_hash, json.dumps(omit(ctx, *omit_keys)))
        await db.expire(_hash, timeout)

    @staticmethod
    async def get_cache(_hash: str, db_provider: DBProvider) -> str:
        """
        gets cache

        @param _hash: (str) hash of request
        @param db: redis instance
        """
        db = db_provider.get_redis()

        return await db.get(_hash, encoding='utf-8')

    @staticmethod
    def make_dto(ctx: dict) -> EndpointCacherDTO:
        endpoint_cacher = EndpointCacherDTO()

        if has(ctx, '_id') or has(ctx, 'id'):
            endpoint_cacher.id = ctx['_id'] if '_id' in ctx else ctx['id']

        if has(ctx, 'service_id'):
            endpoint_cacher.service_id = ctx['service_id']

        if has(ctx, 'timeout'):
            endpoint_cacher.timeout = ctx['timeout']

        if has(ctx, 'response_codes'):
            endpoint_cacher.response_codes = ctx['response_codes']
        
        return endpoint_cacher
