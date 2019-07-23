import bson
import aiohttp
import asyncio
import json
import requests
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

class Api:
  @staticmethod
  async def call(method, url, params=None, data=None, json=None, cookies=None, headers=None, auth=None):
    return await aiohttp.request(method=method, url=url, params=params, data=data, json=json, cookies=cookies, headers=headers, auth=auth)
  
  @staticmethod
  def batch(requests):
    results = []
    for request in requests:
        res = asyncio.run(Api.call(request['method'], request['url'], request['params'], request['data'], request['json'], request['cookies'], request['headers'], request['auth']))
        results.append(res)
    return results

  @staticmethod
  async def batch_async(requests):
    results = []
    for request in requests:
      res = await Api.call(request['method'], request['url'], request['params'], request['data'], request['json'], request['cookies'], request['headers'], request['auth'])
      results.append(res)
    return results
