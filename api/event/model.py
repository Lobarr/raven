import bson
import json
import requests
from cerberus import Validator
from typing import Optional
from aiohttp.client import ClientSession
from api.event import event_schema, event_validator
from api.util import Validate

collection_name = 'event'

class Event:
  @staticmethod
  async def create(ctx: object, db):
    await db.insert_one(ctx)
  
  @staticmethod
  async def update(id: str, ctx: object, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
  
  @staticmethod
  async def get_by_id(id: str, db):
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_by_circuit_breaker_id(id: str, db):
    res = await db.find({'circuit_breaker_id': id})
    return res.to_list(100)
  
  @staticmethod
  async def get_by_target(target: str, db):
    res = await db.find({'target': target})
    return res.to_list(100)
  
  @staticmethod
  async def get_all(db):
    res = await db.find({})
    return res.to_list(100)
  
  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})

  @staticmethod
  async def handle_event(ctx: object):
    res = requests.post(url=ctx['target'], data=ctx['body'], headers=ctx['headers'])
    # TODO send email to admins on failure
