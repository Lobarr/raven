import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.insights.schema import insights_schema, insights_validator

collection_name = 'insights'

class Insights:
  @staticmethod
  async def create(ctx: object, db):
    valid = insights_validator.validate(ctx)
    if valid is True:
      db.insert_one(ctx)
    else:
        raise Exception("Invalid data provided")

  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = insights_validator.validate(ctx)
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
  async def get_by_remote_ip(remote_ip: str, db):
    return await db.find({'remote_ip': remote_ip}).to_list(100)

  @staticmethod
  async def get_by_status_code(status_code: int, db):
    return await db.find({'status_code': status_code}).to_list(100)
  
  @staticmethod
  async def get_by_path(path: str, db):
    return await db.find({'path': path}).to_list(100)
  
  @staticmethod
  async def get_by_method(method: str, db):
    return await db.find({'method': method}).to_list(100)
  
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
