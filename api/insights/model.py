import bson
from api.insights.schema import insights_schema, insights_validator

collection_name = 'insights'

class Insights:
  @staticmethod
  async def create(ctx: object, db):
    await db.insert_one(ctx)

  @staticmethod
  async def update(id: str, ctx: object, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
  
  @staticmethod
  async def get_by_service_id(id: str, db):
    res = db.find({'service_id': id})
    return await res.to_list(100)

  @staticmethod
  async def get_by_scheme(scheme: str, db):
    res = db.find({'scheme': scheme})
    return await res.to_list(100)

  @staticmethod
  async def get_by_id(id: str, db):
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_by_remote_ip(remote_ip: str, db):
    res = db.find({'remote_ip': remote_ip})
    return await res.to_list(100)

  @staticmethod
  async def get_by_status_code(status_code: int, db):
    res = db.find({'status_code': status_code})
    return await res.to_list(100)
  
  @staticmethod
  async def get_by_path(path: str, db):
    res = db.find({'path': path})
    return await res.to_list(100)
  
  @staticmethod
  async def get_by_method(method: str, db):
    res = db.find({'method': method})
    return await res.to_list(100)
  
  @staticmethod
  async def get_all(db):
    res = db.find({})
    return await res.to_list(100)
  
  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})
