from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.service.schema import service_schema, service_validator

collection_name = 'service'

class Service:
  @staticmethod
  async def create(ctx: object, db):
    valid = service_validator.validate(ctx)
    if valid is True:
      db.insert_one(ctx)
    else:
        raise Exception("Invalid data provided")
