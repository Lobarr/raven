import bson
import pydash
import logging
import asyncio
from aioredis import Redis as AioRedis
from cerberus import Validator
from api.rate_limiter.schema import rate_limit_rule_schema, rate_limit_rule_validator, rate_limit_entry_schema, rate_limit_entry_validator
from api.util import Bson, DB
from api.service import Service

endpoint_cache_set = 'endpoint_cache_set'
endpoint_cache_service_id_index = 'endpoint_cache_service_id'
endpoint_cache_endpoint_index = 'endpoint_cache_endpoint_index'

class EndpointCacher:
  @staticmethod
  async def _set_indexes(ctx: object, db: AioRedis):
    for index in [('service_id', endpoint_cache_service_id_index), ('endpoint', endpoint_cache_endpoint_index)]:
      if index[0] in ctx:
        await db.hset(index[1], ctx['_id'], ctx[index[0]])

  @staticmethod
  async def _clear_indexes(_id: str, db: AioRedis):
    for index in [endpoint_cache_endpoint_index, endpoint_cache_service_id_index]:
      await db.hdel(index, _id)

  @staticmethod
  async def _search_indexes(index: str, search: str, db: AioRedis) -> list:
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
    )
  
  @staticmethod
  async def update(_id: str, ctx: object, db: AioRedis):
    await EndpointCacher._set_indexes(pydash.merge(ctx, {'_id': _id}), db)
    await db.hmset_dict(_id, ctx)

  @staticmethod
  async def delete(_id: str, db: AioRedis):
    await asyncio.gather(
      db.delete(_id),
      EndpointCacher._clear_indexes(_id, db),
      db.srem(endpoint_cache_set, _id),
    )

  @staticmethod
  async def get_by_id(_id: str, db: AioRedis) -> object:
    endpoint_cache = await db.hgetall(_id, encoding='utf-8')
    if 'response_codes' in endpoint_cache:
      response_codes_id = endpoint_cache['response_codes']
      response_codes = await db.smembers(response_codes_id, encoding='utf-8')
    return pydash.merge(endpoint_cache, {'response_codes': response_codes})
  
  @staticmethod
  async def get_by_service_id(service_id: str, db: AioRedis) -> list:
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
    endpoint_cache = await db.hgetall(_id, encoding='utf-8')
    if not pydash.has(endpoint_cache, 'response_codes'):
      raise Exception({
        'message': f'Unable to update cache {_id}',
        'status_code': 400
      })
    for status_code in status_codes:
      await db.srem(endpoint_cache['response_codes'], status_code)
