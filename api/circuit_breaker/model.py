import bson
from api.circuit_breaker.schema import circuit_breaker_schema, circuit_breaker_validator

table = 'circuitBreaker'

class CircuitBreaker:
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
  async def get_by_service_id(service_id: str, db):
    res = await db.find({'service_id': service_id})
    return res.to_list(100)

  @staticmethod
  async def get_by_status_code(status_code: int, db):
    res = await db.find({'status_code': status_code})
    return res.to_list(100)
  
  @staticmethod
  async def get_by_method(method: str, db):
    res = await db.find({'method': method})
    return res.to_list(100)

  @staticmethod
  async def get_by_path(path: str, db):
    res = await db.find({'path': path})
    return res.to_list(100)

  @staticmethod
  async def get_by_threshold(threshold: float, db):
    res = await db.find({'threshold': threshold})
    return res.to_list(100)

  @staticmethod
  async def get_all(db):
    res = await db.find({})
    return res.to_list(100)

  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})
