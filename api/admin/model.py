import bson
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from api.admin.schema import admin_schema, admin_validator
from api.util import Password
from api.util.env import RAVEN_ADMIN_PASS, RAVEN_ADMIN_USER

collection_name = 'admin'

class Admin:
  @staticmethod
  async def create(ctx: dict, db):
    """
    creates an admin  
  
    @param ctx: (object) context of admin
    @param db: mongo instance
    """
    ctx['password'] = Password.hash(ctx['password'])
    await db.insert_one(ctx)

  @staticmethod
  async def update(_id: str, ctx: dict, db):
    """
    updates an admin
  
    @param id: (str) id of admin to update
    @param ctx: (object) 
    """
    if 'password' in ctx:
      ctx['password'] = Password.hash(ctx['password'])
    await db.update_one({'_id': bson.ObjectId(_id)}, {'$set': ctx})

  @staticmethod
  async def get_by_id(_id: str, db):
    """
    gets an admin by id
  
  
    @param id: id of admin
    @param db: mongo instance
    """
    return await db.find_one({'_id': bson.ObjectId(_id)})

  @staticmethod
  async def get_by_email(email: str, db):
    """
    gets an admin by email
  
  
    @param email: email of admin
    @param db: mongo instance
    """
    res = db.find({'email': email})
    return await res.to_list(100)
    
  @staticmethod 
  async def get_by_username(username: str, db):
    """
    gets an admin by username
  
  
    @param username: username of admin
    @param db: mongo instance
    """
    res = db.find({'username': username})
    return await res.to_list(100)

  @staticmethod 
  async def verify_password(username: str, password: str, db):
    """
    verfies admin password
  
    @param username: (str) username of admin
    @param password: (str) password to check
    @param db: mongo instance
    """
    admin = await Admin.get_by_username(username, db)
    match = Password.validate(password, admin['password'])
    return match 

  @staticmethod
  async def get_all(db):
    """
    gets all admins
  
    @param db: mongo instance
    """
    res = db.find({})
    return await res.to_list(100) 

  @staticmethod
  async def count(db):
    """
    counts admins
  
    @param db: mongo instance
    """
    return await db.count_documents({})
  
  @staticmethod
  async def remove(_id: str, db):
    """
    removes an id
  
    @param id: (str) id of admin
    @param db: mongo instance
    """
    await db.delete_one({'_id': bson.ObjectId(_id)})
  
  @staticmethod
  async def create_default(db):
    """
    create a default admin if none exists
  
    @param db: mongo instance
    """
    admin_count = await Admin.count(db)
    if admin_count == 0:
      await Admin.create({
        'username': RAVEN_ADMIN_USER,
        'password': RAVEN_ADMIN_PASS
      }, db)
