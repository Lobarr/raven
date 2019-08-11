import os
import asyncio
import aioredis
from celery import Celery
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

#routers
from api.ping import ping_router
from api.service import service_router 
from api.insights import insights_router
from api.request_validator import request_validator_router
from api.admin import admin_router, Admin
from api.rate_limiter import rate_limiter_router
from api.event import event_router
from api.circuit_breaker import circuit_breaker_router
from api.endpoint_cacher import endpoint_cacher_router
from api.proxy import proxy

#utils
from api.util.env import DB, REDIS

async def init():
  is_prod = os.getenv("ENV") is "prod"
  app = web.Application(middlewares=[proxy])
  raven = web.Application()
  app['mongo'] = AsyncIOMotorClient(DB).raven
  app['redis'] = await aioredis.create_redis(REDIS)

  #routes
  routers = [
    admin_router, 
    circuit_breaker_router,
    endpoint_cacher_router,
    event_router,
    insights_router, 
    ping_router, 
    rate_limiter_router, 
    request_validator_router,
    service_router, 
  ]

  for router in routers:
    raven.add_routes(router)

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
  
  await Admin.create_default(app['mongo']['admin'])

  return app


if __name__ == "__main__":
  app = init()
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("API")
  web.run_app(app, port=os.getenv("PORT", 3001), access_log=logger)
