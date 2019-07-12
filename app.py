import os
import asyncio
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import logging
import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

#routers
from api.ping import ping_router
from api.service import service_router 
from api.insights import insights_router
from api.requestvalidator import requestvalidator_router
from api.admin import admin_router, Admin
from api.authservice import authservice_router
from api.ratelimiter import ratelimiter_router

#utils
from api.util.env import DB, REDIS

async def init():
  is_prod = os.getenv("ENV") is "prod"
  app = web.Application()
  raven = web.Application()
  raven['mongo'] = AsyncIOMotorClient(DB).raven
  raven['redis'] = await aioredis.create_redis(REDIS)

  #routes
  raven.add_routes(ping_router)
  raven.add_routes(service_router)
  raven.add_routes(insights_router)
  raven.add_routes(admin_router)
  raven.add_routes(requestvalidator_router)
  raven.add_routes(authservice_router)
  raven.add_routes(ratelimiter_router)
  raven.add_routes([web.static('/dashboard', './client/dist')]) if is_prod else None
  app.add_subapp('/raven', raven)

  #cors
  cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
  })
  for route in list(app.router.routes()):
    cors.add(route)
  
  admin_count = await Admin.count(raven['mongo']['admin'])
  if admin_count == 0:
    await Admin.create({
      'email': 'root@raven.com',
      'username': 'root',
      'password': 'toor'
    }, raven['mongo']['admin'])

  return app


if __name__ == "__main__":
  app = init()
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("API")
  web.run_app(app, port=os.getenv("PORT", 3001), access_log=logger)
