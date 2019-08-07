import json
import base64
from bson import json_util
from api.util import Bson, DB
from aioredis import Redis

class Redis:
  @staticmethod
  async def fetch_members(key, db: Redis):
    return await db.smembers(key, encoding='utf-8')

  @staticmethod
  async def format_response(response):
    response = Bson.to_json(response)
    values = []
    for item in response:
        values.append(item)
    return values
