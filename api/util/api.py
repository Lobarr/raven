import bson
import aiohttp
import json
import requests
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

class Api:
  @staticmethod
  async def call(method, url, params=None, data=None, json=None, cookies=None, headers=None, auth=None):
    async with aiohttp.request(method=method, url=url, params=params, data=data, json=json, cookies=cookies, headers=headers, auth=auth) as resp:
      return resp
    
  @staticmethod
  async def batch(requests):
    results = []
    for i in range(len(headers)):
        res = requests.post(urls[i], headers=headers[i], data=json.dumps(bodies[i]))
        results.append(res)
    return results

  @staticmethod
  async def batch_async(headers, bodies, urls):
    """
    Should accept 3 lists of parameters (list of headers, list of bodies, list of urls) to be run
    """
    results = []
    for i in range(len(headers)):
        res = await ApiUtil.single(headers[i], bodies[i], urls[i])
        results.append(res)
    return results

  #things not done:
  # currently synchronous_batch runs with requests but i am not sure thats the right way to make it synchronous.
  #Should include headers, body, method, and redirect properties from request?
