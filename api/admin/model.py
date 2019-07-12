import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.admin.schema import admin_schema, admin_validator
from api.util import Password

collection_name = 'admin'

class Admin:
  @staticmethod
  async def create(ctx: object, db):
    valid = admin_validator.validate(ctx)
    ctx['password'] = Password.hash(ctx['password'])
    if valid is True:
      await db.insert_one(ctx)
    else:
      raise Exception({
        'messge': 'Invalid data provided',
        'status_code': 400
      })

  @staticmethod
  async def update(id: str, ctx: object, db):
    valid = admin_validator.validate(ctx)
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
  async def get_by_email(email: str, db):
    return await db.find({'email': email}).to_list(100)
    
  @staticmethod 
  async def get_by_username(username: str, db):
    return await db.find({'username': username}).to_list(100)

  @staticmethod 
  async def verify_password(username: str, password: str, db):
    admin = await Admin.get_by_username(username)
    match = await Password.validate(password, admin['hash'])
    return match 

  @staticmethod
  async def get_all(db):
    return await db.find({}).to_list(100) 

  @staticmethod
  async def count(db):
    collection_count = await db.count_documents({})
    return collection_count
  
  @staticmethod
  async def remove(id: str, db):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
    return await db.delete_one({'_id': bson.ObjectId(id)})
