import bson
from motor.motor_asyncio import AsyncIOMotorCollection
from api.insights.schema import insights_schema, insights_validator
from api.service import Service

collection_name = 'insights'

class Insights:
  """
  creates an insight

  @param ctx: (dict) context to create insight with
  @param insights_db: mongo collection instance
  @param service_db: mongo collection isntance
  """
  @staticmethod
  async def create(ctx: object, insights_db: AsyncIOMotorCollection, service_db: AsyncIOMotorCollection):
    if 'service_id' in ctx:
      await Service.check_exists(ctx['service_id'], service_db)
    await insights_db.insert_one(ctx)

  """
  updates an insight

  @param id: (str) id of insight
  @param db: mongo collection instance
  """
  @staticmethod
  async def update(_id: str, ctx: object, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$set': ctx})
  
  """
  gets insights by service id

  @param id: (str) id to get insights by 
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_service_id(_id: str, db: AsyncIOMotorCollection):
    res = db.find({'service_id': _id})
    return await res.to_list(100)

  """
  gets insights by scheme

  @param scheme: (str) scheme to get insights by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_scheme(scheme: str, db: AsyncIOMotorCollection):
    res = db.find({'scheme': scheme})
    return await res.to_list(100)

  """
  gets insights by id

  @param id: (str) id to get insights by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_id(_id: str, db: AsyncIOMotorCollection):
    return await db.find_one({'_id': bson.ObjectId(_id)})
  
  """
  gets insights by remote ip

  @param remote_id: (str) remote_ip to get insights by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_remote_ip(remote_ip: str, db: AsyncIOMotorCollection):
    res = db.find({'remote_ip': remote_ip})
    return await res.to_list(100)

  """
  gets insights by status code

  @param status_code: (str) status_code to get insights by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_status_code(status_code: int, db: AsyncIOMotorCollection):
    res = db.find({'status_code': status_code})
    return await res.to_list(100)
  
  """
  gets insights by path

  @param path: (str) path to get insights by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_path(path: str, db: AsyncIOMotorCollection):
    res = db.find({'path': path})
    return await res.to_list(100)
  
  """
  gets insights by method

  @param method: (str) method to get insights by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_method(method: str, db: AsyncIOMotorCollection):
    res = db.find({'method': method})
    return await res.to_list(100)
  
  """
  gets all insights 

  @param db: mongo collection instance
  """
  @staticmethod
  async def get_all(db: AsyncIOMotorCollection):
    res = db.find({})
    return await res.to_list(100)
  
  """
  removes an insight

  @param id: (str) id of insight
  @param db: mongo collection instance
  """
  @staticmethod
  async def remove(_id: str, db: AsyncIOMotorCollection):
    await db.delete_one({'_id': bson.ObjectId(_id)})
