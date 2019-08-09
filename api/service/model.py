import bson
from motor.motor_asyncio import AsyncIOMotorCollection
from .schema import service_schema, service_validator

collection_name = 'service'

class Service:
  """
  creates a service

  @param ctx: (dict) context of service to create
  @param db: mongo collection instance
  """
  @staticmethod
  async def create(ctx: object, db: AsyncIOMotorCollection):
    await db.insert_one(ctx)
  
  """
  updates a service
  
  @param id: (str) id of service to update
  @param ctx: (dict) context of fields to update
  @param db: mongo collection instance
  """
  @staticmethod
  async def update(_id: str, ctx: object, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$set': ctx})
  
  """
  gets a service by id

  @param id: (str) id of service to get
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_id(_id: str, db: AsyncIOMotorCollection) -> object:
    return await db.find_one({'_id': bson.ObjectId(_id)})
  
  """
  gets a servie by state

  @param state: (str) state to get service by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_state(state: str, db: AsyncIOMotorCollection) -> list:
    res = db.find({'state': state})
    return await res.to_list(100)
  
    """
  gets a service by secure

  @param secure: (bool) id of secure to get
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_secure(secure: bool, db: AsyncIOMotorCollection) -> list:
    res = db.find({'secure': secure})
    return await res.to_list(100)
  
  """
  gets all services

  @param db: mongo collection instance
  """
  @staticmethod
  async def get_all(db: AsyncIOMotorCollection) -> list:
    res = db.find({})
    return await res.to_list(100)
  
  """
  removes a service

  @param id: (str) id of service to remove
  @param db: mongo collection instance
  """
  @staticmethod
  async def remove(_id: str, db: AsyncIOMotorCollection):
    await db.delete_one({'_id': bson.ObjectId(_id)})
  
  """
  adds a target to a service

  @param id: (str) id of service 
  @param target: (str) target to add to service
  @param db: mongo collection instance
  """
  @staticmethod
  async def add_target(_id: str, target: str, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$push': {'targets': target}})

  """
  removes a target from a service

  @param id: (str) id of service 
  @param target: (str) target to remove from service
  @param db: mongo collection instance
  """
  @staticmethod
  async def remove_target(_id: str, target: str, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$pull': {'targets': target}})
  
  """
  advances target to next in list

  @param id: (str) id of service 
  @param db: mongo collection instance
  """
  @staticmethod
  async def advance_target(_id: str, db: AsyncIOMotorCollection):
    ctx = {}
    service = await Service.get_by_id(_id, db)
    if 'targets' in service and len(service['targets']) > 0:
      next_target_index = service['cur_target_index'] + 1
      if next_target_index  <= len(service['targets']) - 1:
        ctx['cur_target_index'] = next_target_index
      else:
        ctx['cur_target_index'] = 0
      await Service.update(_id, ctx, db)

  """
  adds a whitelisted host to a service

  @param id: (str) id of service 
  @param host: (str) host to add to service
  @param db: mongo collection instance
  """
  @staticmethod
  async def add_whitelist(_id: str, host: str, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$push': {'whitelisted_hosts': host}})
  
  """
  removes a whitelisted host from a service

  @param id: (str) id of service 
  @param host: (str) host to remove from service
  @param db: mongo collection instance
  """
  @staticmethod
  async def remove_whitelist(_id: str, host: str, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$pull': {'whitelisted_hosts': host}})
  
  """
  adds a blacklisted host to a service

  @param id: (str) id of service 
  @param host: (str) host to add to service
  @param db: mongo collection instance
  """
  @staticmethod
  async def add_blacklist(_id: str, host: str, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$push': {'blacklisted_hosts': host}})
  
  """
  removes a blacklisted host from a service

  @param id: (str) id of service 
  @param host: (str) host to remove from service
  @param db: mongo collection instance
  """
  @staticmethod
  async def remove_blacklist(_id: str, host: str, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$pull': {'blacklisted_hosts': host}})

  """
  checks if a service exists 

  @param id: (str) id of service
  @param db: mongo collection instance
  """
  @staticmethod
  async def check_exists(_id, db: AsyncIOMotorCollection):
    service = await Service.get_by_id(_id, db)
    if service is None:
      raise Exception({
        'message': 'Service id provided does not exist',
        'status_code': 400
      })
