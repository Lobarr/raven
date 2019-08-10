import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.admin.schema import admin_schema, admin_validator
from api.util import Password
from api.util.env import RAVEN_ADMIN_PASS, RAVEN_ADMIN_USER

collection_name = 'admin'

class Admin:
  """
  creates an admin  

  @param ctx: (object) context of admin
  @param db: mongo instance
  """
  @staticmethod
  async def create(ctx: dict, db):
    ctx['password'] = Password.hash(ctx['password'])
    await db.insert_one(ctx)

  """
  updates an admin

  @param id: (str) id of admin to update
  @param ctx: (object) 
  """
  @staticmethod
  async def update(id: str, ctx: dict, db):
    if 'password' in ctx:
      ctx['password'] = Password.hash(ctx['password'])
    await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})

  """
  gets an admin by id


  @param id: id of admin
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_id(id: str, db):
    return await db.find_one({'_id': bson.ObjectId(id)})

  """
  gets an admin by email


  @param email: email of admin
  @param db: mongo instance
  """
  @staticmethod
  async def get_by_email(email: str, db):
    res = db.find({'email': email})
    return await res.to_list(100)
    
  """
  gets an admin by username


  @param username: username of admin
  @param db: mongo instance
  """
  @staticmethod 
  async def get_by_username(username: str, db):
    res = db.find({'username': username})
    return await res.to_list(100)

  """
  verfies admin password

  @param username: (str) username of admin
  @param password: (str) password to check
  @param db: mongo instance
  """
  @staticmethod 
  async def verify_password(username: str, password: str, db):
    admin = await Admin.get_by_username(username, db)
    match = Password.validate(password, admin['password'])
    return match 

  """
  gets all admins

  @param db: mongo instance
  """
  @staticmethod
  async def get_all(db):
    res = db.find({})
    return await res.to_list(100) 

  """
  counts admins

  @param db: mongo instance
  """
  @staticmethod
  async def count(db):
    return await db.count_documents({})
  
  """
  removes an id

  @param id: (str) id of admin
  @param db: mongo instance
  """
  @staticmethod
  async def remove(id: str, db):
    await db.delete_one({'_id': bson.ObjectId(id)})
  
  """
  create a default admin if none exists

  @param db: mongo instance
  """
  @staticmethod
  async def create_default(db):
    admin_count = await Admin.count(db)
    if admin_count == 0:
      await Admin.create({
        'username': RAVEN_ADMIN_USER,
        'password': RAVEN_ADMIN_PASS
      }, db)
