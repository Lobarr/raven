import asyncio
import aioredis
import bson
import json
import base64
from cerberus import Validator
from api.ratelimiter.schema import rate_limit_rule_schema, rate_limit_rule_validator, rate_limit_entry_schema, rate_limit_entry_validator
from api.util import Bson, Redis

rate_limit_rule_set = 'rate_limit_rules'
rate_limit_entry_set = 'rate_limit_entries'

class RateLimiter:
    
  @staticmethod
  async def create_rule(ctx, db):
    """
    Creates a rate limiter rule.

    @param ctx: (object) data to be inserted
    @param db: (object) db connection
    """
    ctx['_id'] = str(bson.ObjectId())
    await db.set(ctx['_id'], json.dumps(ctx))
    await db.sadd(rate_limit_rule_set, ctx['_id'])

  @staticmethod
  async def update_rule(id, ctx, db):
    """
    Updates a rate limiter rule.

    @param ctx: (object) data to use for update
    @param db: (object) db connection
    """
    ctx['_id'] = id
    await db.set(id, json.dumps(ctx))

  @staticmethod
  async def delete_rule(id, db):
    """
    Deletes a rate limiter rule.

    @param id: (string) the ID of the rate limiter rule to delete
    @param db: (object) db connection
    """
    await db.delete(id)
    await db.srem(rate_limit_rule_set, id)

  @staticmethod
  async def get_rules_by_status_code(status_code: int, db):
    """
    Gets a rate limiter rule by the status code

    @param status_code: (string) status code of the rate limiter rule
    @param db: (object) db connection
    @return: the records with the provided statusCode
    """
    results = await Redis.fetch_members(rate_limit_rule_set, db)
    return list(filter(lambda result: int(result['status_code']) == status_code, results))
          
  
  @staticmethod
  async def get_rules_by_path(path, db):
    """
    Gets a rate limiter rule by the path of the rule

    @param path: (string) path of the rate limiter rule
    @param db: (object) db connection
    @return: the records with the given path
    """
    results = await Redis.fetch_members(rate_limit_rule_set, db)
    return list(filter(lambda result: int(result['path']) == path, results))

  
  @staticmethod
  async def get_all_rules(db):
    """
    Gets a rate limiter rule by the status code

    @param statusCode: (string) status code of the rate limiter rule
    @param db: (object) db connection
    @return: the records with the provided statusCode
    """
    return await Redis.fetch_members(rate_limit_rule_set, db)
          
  @staticmethod
  async def create_entry(ctx, db):
    """
    Creates a rate limiter entry.

    @param ctx: (object) data to be inserted
    @param db: (object) db connection
    """
    await db.set(ctx['host'], json.dumps(ctx))
    await db.sadd(rate_limit_entry_set, ctx['host'])
    
    entry = await db.get(ctx['rule_id'])
    entry_data = json.loads(entry)
    await db.expire(ctx['host'], int(entry_data['time_limit']))
          
  @staticmethod
  async def update_entry(host, ctx, db):
    """
    Updates a rate limiter entry.

    @param ctx: (object) data to use for update
    @param db: (object) db connection
    """
    await db.set(host, json.dumps(ctx))

  @staticmethod
  async def delete_entry(host, db):
    """
    Deletes a rate limiter entry.

    @param host: (string) the hostname of the rate limiter entry to delete
    @param db: (object) db connection
    """
    await db.delete(host)
    await db.srem(rate_limit_entry_set, host)

  @staticmethod
  async def get_all_entries(db):
    """
    Gets all rate limiter entries
    
    @param db: (object) db connection
    @return: the records with the provided statusCode
    """
    return await Redis.fetch_members(rate_limit_entry_set, db)
  
  @staticmethod
  async def increment_entry_count(id, db):
    entry = await db.get(id)
    entry_data = json.loads(entry)
    entry_data['count'] = entry_data['count'] + 1
    await db.set(id, json.dumps(entry_data))
      
  @staticmethod
  async def decrement_entry_count(id, db):
    entry = await db.get(id)
    entry_data = json.loads(entry)
    entry_data['count'] = entry_data['count'] - 1
    await db.set(id, json.dumps(entry_data))
