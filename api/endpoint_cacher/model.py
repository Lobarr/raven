import bson
import pydash
import logging
import asyncio
from aioredis import Redis as AioRedis
from cerberus import Validator
from api.rate_limiter.schema import rate_limit_rule_schema, rate_limit_rule_validator, rate_limit_entry_schema, rate_limit_entry_validator
from api.util import Bson, DB, Async
from api.service import Service

endpoint_cache_set = 'endpoint_cache_set'
endpoint_cache_service_id_index = 'endpoint_cache_service_id'
endpoint_cache_endpoint_index = 'endpoint_cache_endpoint_index'

class EndpointCacher:
  @staticmethod
  async def _set_indexes(ctx: object, db: AioRedis):
    """
    sets secondary indexes
  
    @param ctx: indexess to set 
    @param db: redis instance
    """
    coroutines = []
    for index in [('service_id', endpoint_cache_service_id_index), ('endpoint', endpoint_cache_endpoint_index)]:
      if index[0] in ctx:
        coroutines.append(db.hset(index[1], ctx['_id'], ctx[index[0]]))
    await Async.all(coroutines)

  @staticmethod
  async def _clear_indexes(_id: str, db: AioRedis):
    """
    clears secondary indexes
  
    @param id: id of entity
    @param db: redis instance
    """
    coroutines = []
    for index in [endpoint_cache_endpoint_index, endpoint_cache_service_id_index]:
      coroutines.append(db.hdel(index, _id))
    await Async.all(coroutines)


  @staticmethod
  async def _search_indexes(index: str, search: str, db: AioRedis) -> list:
    """
    searches secondary indexes
  
    @param index: (str) index to search
    @param serach: (str) serach value
    @param db: redis instance
    """
    keys = []
    cur = b'0'
    while cur:
      cur, vals = await db.hscan(index, cur)
      for key in vals:
        if key[1].decode('utf-8') == search:
          keys.append(key[0].decode('utf-8'))
    return keys

  @staticmethod
  async def create(ctx: object, endpoint_cacher_db: AioRedis, service_db):
    """
    creates an endpoint cache
  
    @param ctx: (object) data to be inserted
    @param endpoint_cacher_db: (object) db connection
    @param service_db: (object) db connection
    """
    ctx['_id'] = str(bson.ObjectId())
    if 'service_id' in ctx:
      await Service.check_exists(ctx['service_id'], service_db)
    if 'response_codes' in ctx:
      response_codes = ctx['response_codes']
      response_codes_id = str(bson.ObjectId())
      for response_code in response_codes:
        await endpoint_cacher_db.sadd(response_codes_id, response_code)
      ctx['response_codes'] = response_codes_id
    await asyncio.gather(
      EndpointCacher._set_indexes(ctx, endpoint_cacher_db),
      endpoint_cacher_db.hmset_dict(ctx['_id'], ctx),
      endpoint_cacher_db.sadd(endpoint_cache_set, ctx['_id']),
      endpoint_cacher_db.expire(ctx['_id'], int(ctx['timeout']))
    )
  
  @staticmethod
  async def update(_id: str, ctx: object, db: AioRedis):
    """
    updates an endpoint cache.
  
    @param id: (str) id of endpoint cache to update
    @param ctx: (object) data to use for update
    @param db: (object) db connection
    """
    await EndpointCacher._set_indexes(pydash.merge(ctx, {'_id': _id}), db)
    await db.hmset_dict(_id, ctx)

  @staticmethod
  async def delete(_id: str, db: AioRedis):
    """
    deletes a endpoint cache rule.
  
    @param id: (string) id of endpoint cache to delete
    @param db: (object) db connection
    """
    await asyncio.gather(
      db.delete(_id),
      EndpointCacher._clear_indexes(_id, db),
      db.srem(endpoint_cache_set, _id),
    )

  @staticmethod
  async def get_by_id(_id: str, db: AioRedis) -> object:
    """
    gets endpoint cache by id
  
    @param id: (str) id of endpoint cache
    @param db: db connection
    """
    endpoint_cache = await db.hgetall(_id, encoding='utf-8')
    if 'response_codes' in endpoint_cache:
      response_codes_id = endpoint_cache['response_codes']
      response_codes = await db.smembers(response_codes_id, encoding='utf-8')
    return pydash.merge(endpoint_cache, {'response_codes': response_codes})
  
  @staticmethod
  async def get_by_service_id(service_id: str, db: AioRedis) -> list:
    """
    gets endpoint cache by service id
  
    @param service_id: (str) service id of endpoint cache
    @param db: db connection
    """
    endpoint_caches = []
    endpoint_cache_keys = await EndpointCacher._search_indexes(endpoint_cache_service_id_index, service_id, db)
    for endpoint_cache_key in endpoint_cache_keys:
      ctx = await db.hgetall(endpoint_cache_key, encoding='utf-8')
      if 'response_codes' in ctx:
        response_codes = await db.smembers(ctx['response_codes'], encoding='utf-8')
      endpoint_caches.append(pydash.merge(ctx, {'response_codes': response_codes}))
    return endpoint_caches

  @staticmethod
  async def get_by_endpoint(endpoint: str, db: AioRedis) -> list:
    """
    gets endpoint cache by endpoint
  
    @param endpoint: (str) endpoint to get
    @param db: db connection
    """
    endpoint_caches = []
    endpoint_cache_keys = await EndpointCacher._search_indexes(endpoint_cache_endpoint_index, endpoint, db)
    for endpoint_cache_key in endpoint_cache_keys:
      ctx = await db.hgetall(endpoint_cache_key, encoding='utf-8')
      if 'response_codes' in ctx:
        response_codes = await db.smembers(ctx['response_codes'], encoding='utf-8')
      endpoint_caches.append(pydash.merge(ctx, {'response_codes': response_codes}))
    return endpoint_caches

  @staticmethod
  async def get_all(db: AioRedis) -> list:
    """
    gets all endpoint caches
  
    @param db: db connection
    """
    endpoint_caches = []
    endpoint_cache_keys = await DB.fetch_members(endpoint_cache_set, db)
    for endpoint_cache_key in endpoint_cache_keys:
      ctx = await db.hgetall(endpoint_cache_key, encoding='utf-8')
      if 'response_codes' in ctx:
        response_codes = await db.smembers(ctx['response_codes'], encoding='utf-8')
      endpoint_caches.append(pydash.merge(ctx, {'response_codes': response_codes}))
    return endpoint_caches

  @staticmethod
  async def add_status_codes(status_codes: list, _id: str, db: AioRedis):
    """
    adds status codes to endpoint cache
  
    @param status_codes: (list) status codes to add
    @param id: (str) id of endpoint cache
    @param db: db connection
    """
    endpoint_cache = await db.hgetall(_id, encoding='utf-8')
    if not pydash.has(endpoint_cache, 'response_codes'):
      raise Exception({
        'message': f'Unable to update cache {_id}',
        'status_code': 400
      })
    for status_code in status_codes:
      await db.sadd(endpoint_cache['response_codes'], status_code)
    
  @staticmethod
  async def remove_status_codes(status_codes: list, _id: str, db: AioRedis):
    """
    removes status codes to endpoint cache
  
    @param status_codes: (list) status codes to remove
    @param id: (str) id of endpoint cache
    @param db: db connection
    """
    endpoint_cache = await db.hgetall(_id, encoding='utf-8')
    if not pydash.has(endpoint_cache, 'response_codes'):
      raise Exception({
        'message': f'Unable to update cache {_id}',
        'status_code': 400
      })
    for status_code in status_codes:
      await db.srem(endpoint_cache['response_codes'], status_code)
