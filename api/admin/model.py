import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.admin.schema import admin_schema, admin_validator
from api.util import Password
from api.util.env import RAVEN_ADMIN_PASS, RAVEN_ADMIN_USER

collection_name = 'admin'

class Admin:
  @staticmethod
  async def create(ctx: object, db):
    ctx['password'] = Password.hash(ctx['password'])
    await db.insert_one(ctx)

  @staticmethod
  async def update(id: str, ctx: object, db):
    if 'password' in ctx:
      ctx['password'] = Password.hash(ctx['password'])
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
  
  @staticmethod
  async def get_by_id(id: str, db):
    return await db.find_one({'_id': bson.ObjectId(id)})

  @staticmethod
  async def get_by_email(email: str, db):
    res = db.find({'email': email})
    return await res.to_list(100)
    
  @staticmethod 
  async def get_by_username(username: str, db):
    res = db.find({'username': username})
    return await res.to_list(100)

  @staticmethod 
  async def verify_password(username: str, password: str, db):
    admin = await Admin.get_by_username(username, db)
    match = Password.validate(password, admin['password'])
    return match 

  @staticmethod
  async def get_all(db):
    res = db.find({})
    return await res.to_list(100) 

  @staticmethod
  async def count(db):
    return await db.count_documents({})
  
  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})
  
  @staticmethod
  async def create_default(db):
    admin_count = await Admin.count(db)
    if admin_count == 0:
      await Admin.create({
        'username': RAVEN_ADMIN_USER,
        'password': RAVEN_ADMIN_PASS
      }, db)
