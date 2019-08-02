import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.service.schema import service_schema, service_validator
from api.util import Validate, Crypt

collection_name = 'service'

class Service:
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
  async def get_by_state(state: str, db):
    res = db.find({'state': state})
    return await res.to_list(100)

  @staticmethod
  async def get_by_secure(secure: bool, db):
    res = db.find({'secure': secure})
    return await res.to_list(100)
  
  @staticmethod
  async def get_all(db):
    res = db.find({})
    return await res.to_list(100)
  
  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def add_target(id: str, target: str, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$push': {'targets': target}})

  @staticmethod
  async def remove_target(id: str, target: str, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$pull': {'targets': target}})
  
  @staticmethod
  async def advance_target(id: str, db):
    ctx = {}
    service = await Service.get_by_id(id, db)
    if 'targets' in service and len(service['targets']) > 0:
      next_target_index = service['cur_target_index'] + 1
      if next_target_index  <= len(service['targets']) - 1:
        ctx['cur_target_index'] = next_target_index
      else:
        ctx['cur_target_index'] = 0
      await Service.update(id, ctx, db)

  @staticmethod
  async def add_whitelist(id: str, host: str, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$push': {'whitelisted_hosts': host}})
  
  @staticmethod
  async def remove_whitelist(id: str, host: str, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$pull': {'whitelisted_hosts': host}})
  
  @staticmethod
  async def add_blacklist(id: str, host: str, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$push': {'blacklisted_hosts': host}})
  
  @staticmethod
  async def remove_blacklist(id: str, host: str, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$pull': {'blacklisted_hosts': host}})

  @staticmethod
  async def check_exists(service_id, db):
    service = await Service.get_by_id(service_id, db)
    print(service_id, service)
    if service is None:
      raise Exception({
        'message': 'Service id provided does not exist',
        'status_code': 400
      })
