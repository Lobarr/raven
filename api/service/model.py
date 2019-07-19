import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.service.schema import service_schema, service_validator
from api.util import Validate, Crypt

collection_name = 'service'

class Service:
  @staticmethod
  async def create(ctx: object, db):
    valid = service_validator.validate(ctx)
    if valid is True:
      await db.insert_one(ctx)
    else:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
  
  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = service_validator.validate(ctx)
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
    Validate.object_id(id)
    await db.delete_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def add_target(id: str, target: str, db):
    Validate.object_id(id)
    await db.update_one({'_id': bson.ObjectId(id)}, {'$push': {'targets': target}})

  @staticmethod
  async def remove_target(id: str, target: str, db):
    Validate.object_id(id)
    await db.update_one({'_id': bson.ObjectId(id)}, {'$pull': {'targets': target}})
  
  @staticmethod
  async def add_whitelist(id: str, host: str, db):
    Validate.object_id(id)
    await db.update_one({'_id': bson.ObjectId(id)}, {'$push': {'whitelisted_hosts': host}})
  
  @staticmethod
  async def remove_whitelist(id: str, host: str, db):
    Validate.object_id(id)
    await db.update_one({'_id': bson.ObjectId(id)}, {'$pull': {'whitelisted_hosts': host}})
  
  @staticmethod
  async def add_blacklist(id: str, host: str, db):
    Validate.object_id(id)
    await db.update_one({'_id': bson.ObjectId(id)}, {'$push': {'blacklisted_hosts': host}})
  
  @staticmethod
  async def remove_blacklist(id: str, host: str, db):
    Validate.object_id(id)
    await db.update_one({'_id': bson.ObjectId(id)}, {'$pull': {'blacklisted_hosts': host}})

  @staticmethod
  def verify_message(message: object, signature: str, public_key: str):
    return Crypt.verify(message, signature, public_key)
