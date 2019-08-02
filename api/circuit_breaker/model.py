import bson
from api.service import Service
from api.circuit_breaker.schema import circuit_breaker_schema, circuit_breaker_validator

table = 'circuitBreaker'

class CircuitBreaker:
  @staticmethod
  async def create(ctx: object, circuit_breaker_db, service_db):
    if 'service_id' in ctx:
      await Service.check_exists(ctx['service_id'], service_db)
    await circuit_breaker_db.insert_one(ctx)  

  @staticmethod
  async def update(id: str, ctx: object, db):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
  
  @staticmethod
  async def get_by_id(id: str, db):
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_by_service_id(service_id: str, db):
    res = db.find({'service_id': service_id})
    return await res.to_list(100)

  @staticmethod
  async def get_by_status_code(status_code: int, db):
    res = db.find({'status_code': status_code})
    return await res.to_list(100)
  
  @staticmethod
  async def get_by_method(method: str, db):
    res = db.find({'method': method})
    return await res.to_list(100)

  @staticmethod
  async def get_by_path(path: str, db):
    res = db.find({'path': path})
    return await res.to_list(100)

  @staticmethod
  async def get_by_threshold(threshold: float, db):
    res = db.find({'threshold': threshold})
    return await res.to_list(100)

  @staticmethod
  async def get_all(db):
    res = db.find({})
    return await res.to_list(100)

  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})

  @staticmethod
  async def check_exists(circuit_breaker_id, db):
    circuit_breaker = await CircuitBreaker.get_by_id(circuit_breaker_id, db)
    if circuit_breaker == None:
      raise Exception({
        'message': 'Circuit breaker id provided does not exist',
        'status_code': 400
      })
