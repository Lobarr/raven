import bson
from motor.motor_asyncio import AsyncIOMotorCollection
from api.service import Service

class CircuitBreaker:
  """
  creates a circuit breaker

  @param ctx: (object) context to create 
  @param circuit_breaker_db: mongo instance
  @param service_db: mongo instance
  """
  @staticmethod
  async def create(ctx: object, circuit_breaker_db: AsyncIOMotorCollection, service_db: AsyncIOMotorCollection):
    if 'service_id' in ctx:
      await Service.check_exists(ctx['service_id'], service_db)
    await circuit_breaker_db.insert_one(ctx)  

  """
  updates circuit breaker

  @param id: (str) id of circuit breaker
  @param ctx: (object) context of update
  @param db: mongo instance
  """
  @staticmethod
  async def update(id: str, ctx: object, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
  
  """
  gets cirbuit breaker by id

  @param id: (str) id of cirbuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_id(id: str, db: AsyncIOMotorCollection):
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  """
  gets cirbuit breaker by service id

  @param service_id: (str) service id of cirbuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_service_id(service_id: str, db: AsyncIOMotorCollection):
    res = db.find({'service_id': service_id})
    return await res.to_list(100)

  """
  gets cirbuit breaker by status code

  @param status_code: (int) status code of cirbuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_status_code(status_code: int, db: AsyncIOMotorCollection):
    res = db.find({'status_code': status_code})
    return await res.to_list(100)
  
  """
  gets cirbuit breaker by method

  @param metod: (str) method of cirbuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_method(method: str, db: AsyncIOMotorCollection):
    res = db.find({'method': method})
    return await res.to_list(100)

  """
  gets cirbuit breaker by path

  @param path: (str) path of cirbuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_path(path: str, db: AsyncIOMotorCollection):
    res = db.find({'path': path})
    return await res.to_list(100)

  """
  gets cirbuit breaker by threshold

  @param threshold: (float) threshold of cirbuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_threshold(threshold: float, db: AsyncIOMotorCollection):
    res = db.find({'threshold': threshold})
    return await res.to_list(100)

  """
  gets all circuit breakers

  @param db: mongo instance
  """
  @staticmethod
  async def get_all(db: AsyncIOMotorCollection):
    res = db.find({})
    return await res.to_list(100)

  """
  removes a cirbuit breaker

  @param id: (str) id of circuit breaker
  @param db: mongo instance
  """
  @staticmethod
  async def remove(id: str, db: AsyncIOMotorCollection):
    await db.delete_one({'_id': bson.ObjectId(id)})

  @staticmethod
  async def check_exists(circuit_breaker_id: str, db: AsyncIOMotorCollection):
    circuit_breaker = await CircuitBreaker.get_by_id(circuit_breaker_id, db)
    if circuit_breaker is None:
      raise Exception({
        'message': 'Circuit breaker id provided does not exist',
        'status_code': 400
      })
