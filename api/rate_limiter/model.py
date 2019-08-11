import bson
import pydash
import asyncio
from aioredis import Redis as AioRedis
from cerberus import Validator
from api.rate_limiter.schema import rate_limit_rule_schema, rate_limit_rule_validator, rate_limit_entry_schema, rate_limit_entry_validator
from api.util import Bson, DB, Async

rules_set = 'rules_set'
rule_path_index = 'rule_path_index'
rule_host_index = 'rule_host_index'
rule_status_code_index = 'rule_status_code_index'
entry_set = 'entries_set'
entry_rule_id_index = 'entry_rule_id_index'
entry_host_index = 'entry_host_index'

class RateLimiter:
  @staticmethod
  async def _set_indexes(ctx: object, db: AioRedis):
    """
    sets secondary indexes

    @param ctx: indexess to set 
    @param db: redis instance
    """
    coroutines = []
    for index in [('path', rule_path_index), ('host', rule_host_index), ('status_code', rule_status_code_index)]:
      if index[0] in ctx:
        coroutines.append(db.hset(index[1], ctx['_id'], ctx[index[0]]))
    for index in [('rule_id', entry_rule_id_index), ('host', entry_host_index)]:
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
    for index in [rule_path_index, rule_host_index, rule_status_code_index, entry_rule_id_index, entry_host_index]:
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
  async def create_rule(ctx: object, db: AioRedis):
    """
    Creates a rate limiter rule.

    @param ctx: (object) data to be inserted
    @param db: (object) db connection
    """
    ctx['_id'] = str(bson.ObjectId())
    await asyncio.gather(
      RateLimiter._set_indexes(ctx, db),
      db.hmset_dict(ctx['_id'], ctx),
      db.sadd(rules_set, ctx['_id']),
    )

  @staticmethod
  async def update_rule(_id: str, ctx: object, db: AioRedis):
    """
    Updates a rate limiter rule.

    @param id: (str) id of rule to update
    @param ctx: (object) data to use for update
    @param db: (object) db connection
    """
    await asyncio.gather(
      RateLimiter._set_indexes(pydash.merge(ctx, {'_id': _id}), db),
      db.hmset_dict(_id, ctx)
    )

  @staticmethod
  async def delete_rule(_id: str, db: AioRedis):
    """
    Deletes a rate limiter rule.

    @param id: (string) the ID of the rate limiter rule to delete
    @param db: (object) db connection
    """
    await asyncio.gather(
      db.delete(_id),
      RateLimiter._clear_indexes(_id, db),
      db.srem(rules_set, _id)
    )

  @staticmethod
  async def get_rule_by_id(_id: str, db: AioRedis) -> object:
    """
    gets rule by id

    @param id: (str) id of rule
    @param db: db connection
    """
    return await db.hgetall(_id, encoding='utf-8')

  @staticmethod
  async def get_rule_by_status_code(status_code: int, db: AioRedis) -> list:
    """
    Gets a rate limiter rule by the status code

    @param status_code: (string) status code of the rate limiter rule
    @param db: (object) db connection
    @return: the records with the provided status_code
    """
    keys = await RateLimiter._search_indexes(rule_status_code_index, status_code, db)
    coroutines = []
    for key in keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)
  
  @staticmethod
  async def get_rule_by_path(path, db) -> list:
    """
    Gets a rate limiter rule by the path of the rule

    @param path: (string) path of the rate limiter rule
    @param db: (object) db connection
    @return: the records with the given path
    """
    keys = await RateLimiter._search_indexes(rule_path_index, path, db)
    coroutines = []
    for key in keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)


  @staticmethod
  async def get_rule_by_host(host: str, db: AioRedis) -> list:
    """
    gets rules by host

    @param host: (str) host to get
    @param db: db connection
    """
    keys = await RateLimiter._search_indexes(rule_host_index, host, db)
    coroutines = []
    for key in keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)
  
  @staticmethod
  async def get_all_rules(db: AioRedis) -> list:
    """
    gets all rules

    @param db: db connection
    """
    rules_keys = await DB.fetch_members(rules_set, db)
    coroutines = []
    for key in rules_keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)
          
  @staticmethod
  async def create_entry(ctx, db):
    """
    Creates a rate limiter entry.

    @param ctx: (object) data to be inserted
    @param db: (object) db connection
    """
    ctx['_id'] = str(bson.ObjectId())
    await asyncio.gather(
      RateLimiter._set_indexes(ctx, db),
      db.hmset_dict(ctx['_id'], ctx),
      db.sadd(entry_set, ctx['_id']),
      db.expire(ctx['_id'], int(ctx['timeout']))
    )
          
  @staticmethod
  async def update_entry(_id, ctx, db):
    """
    Updates a rate limiter entry.

    @param ctx: (object) data to use for update
    @param db: (object) db connection
    """
    await asyncio.gather(
      RateLimiter._set_indexes(pydash.merge(ctx, {'_id': _id}), db),
      db.hmset_dict(_id, ctx)
    )

  @staticmethod
  async def delete_entry(_id, db):
    """
    Deletes a rate limiter entry.

    @param host: (string) the hostname of the rate limiter entry to delete
    @param db: (object) db connection
    """
    await asyncio.gather(
      db.delete(_id),
      RateLimiter._clear_indexes(_id, db),
      db.srem(entry_set, _id)
    )

  @staticmethod
  async def get_all_entries(db):
    """
    Gets all rate limiter entries
    
    @param db: (object) db connection
    @return: the records with the provided statusCode
    """
    entries_keys = await DB.fetch_members(entry_set, db)
    coroutines = []
    for key in entries_keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)

  @staticmethod
  async def get_entry_by_id(_id: str, db: AioRedis):
    """
    gets entry by id

    @param id: (str) id of entry
    @param db: redis instance
    """
    return await db.hgetall(_id, encoding='utf-8')

  @staticmethod
  async def get_entry_by_rule_id(rule_id: str, db: AioRedis):
    """
    gets entry by rule id

    @param rule_id: (str) id of entry
    @param db: redis instance
    """
    entries_keys = await RateLimiter._search_indexes(entry_rule_id_index, rule_id, db)
    coroutines = []
    for key in entries_keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)

  @staticmethod
  async def get_entry_by_host(host: str, db: AioRedis):
    """
    gets entry by host

    @param host: (str) host of entry
    @param db: redis instance
    """
    entries_keys = await RateLimiter._search_indexes(entry_host_index, host, db)
    coroutines = []
    for key in entries_keys:
      coroutines.append(db.hgetall(key, encoding='utf-8'))
    return await Async.all(coroutines)
  
  @staticmethod
  async def increment_entry_count(_id: str, db: AioRedis):
    """
    increments entry count
  
    @param id: (str) id of entry
    @param db: redis instance
    """
    await db.hincrby(_id, 'count', 1)
      
  @staticmethod
  async def decrement_entry_count(_id, db):
    """
    decrements entry count
  
    @param id: (str) id of entry
    @param db: redis instance
    """
    await db.hincrby(_id, 'count', -1)
