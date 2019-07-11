import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.service.schema import service_schema, service_validator

collection_name = 'service'

class Service:
  @staticmethod
  async def create(ctx: object, db):
    valid = service_validator.validate(ctx)
    if valid is True:
      await db.insert_one(ctx)
    else:
      raise Exception({
        'messge': 'Invalid data provided',
        'sttus_code': 400
      })
  
  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = service_validator.validate(ctx)
    if valid is True and bson.ObjectId.is_valid(id) is True:
      await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
    else:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
  
  @staticmethod
  async def get_by_id(id: str, db):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'messge': 'Invalid data provided',
        'sttus_code': 400
      })
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_by_state(state: str, db):
    return await db.find({'state': state}).to_list(100)

  @staticmethod
  async def get_by_secure(secure: bool, db):
    return await db.find({'secure': secure}).to_list(100)
  
  @staticmethod
  async def get_all(db):
    return await db.find({}).to_list(100)
  
  @staticmethod
  async def remove(id: str, db):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
    return await db.delete_one({'_id': bson.ObjectId(id)})
