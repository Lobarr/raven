import os
import asyncio
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

#utils
from api.util.env import DB

async def init():
  is_prod = os.getenv("ENV") is "prod"
  app = web.Application()
  raven = web.Application()
  raven['mongo'] = AsyncIOMotorClient(DB).raven

  #routes
  raven.add_routes(ping_router)
  raven.add_routes(service_router)
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
  
  return app

if __name__ == "__main__":
  app = init()
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("API")
  web.run_app(app, port=os.getenv("PORT", 3001), access_log=logger)
