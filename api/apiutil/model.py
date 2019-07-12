import bson
from typing import Optional
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import json
import requests

class ApiUtil:
    
  @staticmethod
  async def single(headers, body, url):
    async with aiohttp.ClientSession() as session:
      # need to have a way to check the http method, not all will be post?
      # pass method as an argument? each different method has a different function call
      async with session.post(url, data=json.dumps(body), headers=headers) as resp:
        if resp.status < 200 or resp.status > 299:
          raise Exception({
            'message': 'Api call unsuccessful',
            'status_code': 400
          })
        return await response.read()
    
  @staticmethod
  async def single_rpc(url, headers, params, id, rpc_method):
    # tried to write this quickly, not sure if all of these params should be passed
    async with aiohttp.ClientSession() as session:
      payload = {
          "jsonrpc": "2.0",
          "method": rpc_method,
          "params": params,
          "id": id
      }
      async with session.post(url, data=json.dumps(payload), headers=headers) as resp:
        if resp.status < 200 or resp.status > 299:
          raise Exception({
            'message': 'Api call unsuccessful',
            'status_code': 400
          })
        return await response.read()    
    
  @staticmethod
  async def synchronous_batch(headers, bodies, urls):
    """
    Should accept 3 lists of parameters (list of headers, list of bodies, list of urls) to be run
    """
    # i wrote this with requests because we want it to be synchronous but not sure that is correct.
    results = []
    for i in range(len(headers)):
        res = requests.post(urls[i], headers=headers[i], data=json.dumps(bodies[i]))
        results.append(res)
    return results

  @staticmethod
  async def concurrent_batch(headers, bodies, urls):
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