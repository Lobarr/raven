import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.circuitBreaker.schema import circuitBreaker_schema, circuitBreaker_validator

collection_name = 'circuitBreaker'

class CircuitBreaker:
  @staticmethod
  async def create(ctx: object, db):
    valid = circuitBreaker_validator.validate(ctx)
    if valid is True:
      await db.insert_one(ctx)
    else:
      raise Exception({
        'messge': 'Invalid data provided',
        'sttus_code': 400
      })
  
  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = circuitBreaker_validator.validate(ctx)
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
        'message': 'Invalid data provided',
        'sttus_code': 400
      })
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_by_service_id(service_id: str, db):
    return await db.find({'service_id': service_id}).to_list(100)

  @staticmethod
  async def get_by_status_code(status_code: int, db):
    return await db.find({'status_code': status_code}).to_list(100)
  
  @staticmethod
  async def get_by_method(method: str, db):
    return await db.find({'method': method}).to_list(100)

@staticmethod
  async def get_by_path(path: str, db):
    return await db.find({'path': path}).to_list(100)

@staticmethod
  async def get_by_threshold_percent(threshold_percent: float, db):
    return await db.find({'threshold_percent': threshold_percent}).to_list(100)

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
