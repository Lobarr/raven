import os
import asyncio
import logging
import aiohttp_cors
from aiohttp import web

#routers
from api.ping import ping_router

is_prod = os.getenv("ENV") is "prod"

if __name__ == "__main__":
  app = web.Application()
  raven = web.Application()
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("API")


  raven.add_routes(ping_router)
  raven.add_routes([web.static('/dashboard', './client/dist')]) if is_prod else None

  app.add_subapp('/raven', raven)
  cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
  })

  for route in list(app.router.routes()):
    cors.add(route)
   
  web.run_app(app, port=os.getenv("PORT", 3001), access_log=logger)
