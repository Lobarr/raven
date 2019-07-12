import bson
from typing import Optional
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import json

from api.authservice.schema import authservice_schema, authservice_validator

collection_name = 'authservice'

class Authservice:
  @staticmethod
  async def create(ctx: object, db):
    valid = authservice_validator.validate(ctx)
    if valid is True:
      db.insert_one(ctx)
    else:
        raise Exception({
          'message': 'Invalid data provided',
          'status_code': 400
        })

  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = authservice_validator.validate(ctx)
    if valid is True and bson.ObjectId.is_valid(id) is True:
      await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
    else:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
  
  @staticmethod
  async def get_by_id(id: str, db):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'messge': 'Invalid data provided',
        'sttus_code': 400
      })
    return await db.find_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def get_all(db):
    return await db.find({}).to_list(100)
  
  @staticmethod
  async def remove(id: str, db):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
    return await db.delete_one({'_id': bson.ObjectId(id)})

  @staticmethod
  async def authorize_token(token, id, db):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
      
    # construct a call based on stored headers/body and current_target  
    # also add the Authorization header w the token
    target = await Authservice.get_by_id(id, db)
    headers = target['headers']
    headers['Authorization'] = 'Bearer ' + token
    body = target['body']
    url = target['current_target']
    
    # so long as this returns a 2xx response we assume everything is good
    async with aiohttp.ClientSession() as session:
      async with session.post(url, data=json.dumps(body), headers=headers) as resp:
        if resp.status < 200 or resp.status > 299:
          raise Exception({
            'message': 'Jwt is invalid',
            'status_code': 400
          })
