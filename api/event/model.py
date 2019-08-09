import bson
import json
import requests
from cerberus import Validator
from motor.motor_asyncio import AsyncIOMotorCollection
from aiohttp.client import ClientSession
from api.event import event_schema, event_validator
from api.util import Validate, Api
from api.circuit_breaker import CircuitBreaker

collection_name = 'event'

class Event:
  """
  creates an event

  @param ctx: (dict) event to create
  @param event_db: mongo collection instance
  @param circuit_breaker_db: mongo collection instance
  """
  @staticmethod
  async def create(ctx: object, event_db: AsyncIOMotorCollection, circuit_breaker_db: AsyncIOMotorCollection):
    if 'circuit_breaker_id' in ctx:
      await CircuitBreaker.check_exists(ctx['circuit_breaker_id'], circuit_breaker_db)
    await event_db.insert_one(ctx)
  
  """
  updates an event

  @param id: (str) id of event
  @param ctx: (dict) fields to update
  @param db: mongo collection instance
  """
  @staticmethod
  async def update(id: str, ctx: object, db: AsyncIOMotorCollection):
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
  
  """
  gets event by id

  @param id: (str) id to get event by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_id(id: str, db: AsyncIOMotorCollection):
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  """
  gets event by circuit breaker id

  @param id: (str) circuit breaker id to get event by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_circuit_breaker_id(id: str, db: AsyncIOMotorCollection):
    res = db.find({'circuit_breaker_id': id})
    return await res.to_list(100)
  
  """
  gets event by target

  @param target: (str) target to get event by
  @param db: mongo collection instance
  """
  @staticmethod
  async def get_by_target(target: str, db: AsyncIOMotorCollection):
    res = db.find({'target': target})
    return await res.to_list(100)
  
  """
  gets all events

  @param db: mongo collection instance
  """
  @staticmethod
  async def get_all(db: AsyncIOMotorCollection):
    res = db.find({})
    return await res.to_list(100)
  
  """
  removes event

  @param id: (str) id of event
  @param db: mongo collection instance

  """
  @staticmethod
  async def remove(id: str, db: AsyncIOMotorCollection):
    await db.delete_one({'_id': bson.ObjectId(id)})

  """
  handles event

  @param ctx: (dict) body of event to handle
  """
  @staticmethod
  async def handle_event(ctx: object):
    res = await Api.call(method='post', url=ctx['target'], data=ctx['body'], headers=ctx['headers'])
    # TODO send email to admins on failure
