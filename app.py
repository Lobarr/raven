from api.service import service_router
from api.util.env import DB, REDIS
from api.util.auth_middleware import auth_middleware
from api.proxy import proxy
from api.endpoint_cacher import endpoint_cacher_router
from api.circuit_breaker import circuit_breaker_router
from api.event import event_router
from api.rate_limiter import rate_limiter_router
from api.admin import admin_router, Admin
from api.request_validator import request_validator_router
from api.insights import insights_router
from api.ping import ping_router
from celery import Celery
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web
from dotenv import load_dotenv

import aiohttp_cors
import aioredis
import asyncio
import logging
import os



load_dotenv()

async def init_db_conns():
    mongo = AsyncIOMotorClient(DB).raven
    redis = await aioredis.create_redis(REDIS)
    return {
        'mongo': mongo,
        'redis': redis
    }

def attach_db_conns_to_app(app: web.Application, db_conns: dict):
    for db_name, db_conn in db_conns.items():
        app[db_name] = db_conn

def init_cors(app: web.Application):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)

def attach_routes_to_app(app: web.Application):
    is_prod = os.getenv("ENV") is "prod"
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
        app.add_routes(router)
    
    is_prod and app.add_routes([web.static('/dashboard', './client/dist')])


async def init():
    app = web.Application(middlewares=[proxy])
    raven = web.Application(middlewares=[auth_middleware])
    db_conns = await init_db_conns()

    attach_db_conns_to_app(app, db_conns)
    attach_db_conns_to_app(raven, db_conns)
    attach_routes_to_app(raven)
    app.add_subapp('/raven', raven)
    init_cors(app)
    await Admin.create_default(app['mongo']['admin'])

    return app


if __name__ == "__main__":
    app = init()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("API")
    web.run_app(app, port=os.getenv("PORT", 3001), access_log=logger)
