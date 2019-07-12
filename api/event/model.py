import bson
import json
from cerberus import Validator
from typing import Optional
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient

from api.event import event_schema, event_validator
from api.util import Validate

collection_name = 'event'

class Event:
  @staticmethod
  async def create(ctx: object, db):
    print(ctx)
    valid = event_validator.validate(ctx)
    if valid is True:
      await db.insert_one(ctx)
    else:
      raise Exception({
        'messge': 'Invalid data provided',
        'status_code': 400
      })
  
  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = event_validator.validate(ctx)
    Validate.object_id(id)
    if valid is True:
      await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
    else:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
  
  @staticmethod
  async def get_by_id(id: str, db):
    Validate.object_id(id)
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_by_circuit_breaker_id(id: str, db):
    return await db.find({'circuit_breaker_id': id}).to_list(100)
  
  @staticmethod
  async def get_all(db):
    return await db.find({}).to_list(100)
  
  @staticmethod
  async def remove(id: str, db):
    Validate.object_id(id)
    await db.delete_one({'_id': bson.ObjectId(id)})

  @staticmethod
  async def handle_event(ctx: object):
    async with ClientSession() as session:
      async with session.post(ctx['target'], data=json.dumps(ctx['body']), headers=ctx['headers']) as resp:
          pass
