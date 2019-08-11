import bson
import aiohttp
import asyncio
import json
import requests
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from api.util import Bytes, Async

class Api:
  @staticmethod
  async def call(method=None, url=None, params=None, data=None, json=None, cookies=None, headers=None, auth=None):
    """
    makes a request
  
    @returns: request response
    """
    async with aiohttp.request(method=method, url=url, params=params, data=data, json=json, cookies=cookies, headers=headers, auth=auth) as response:
      return {
        'status': response.status,
        'reason': response.reason,
        'method': response.method,
        'url': str(response.url),
        'cookies': dict(response.cookies),
        'headers': dict(response.headers),
        'content_type': response.content_type,
        'content_length': response.content_length,
        'body_bytes': Bytes.encode_bytes(await response.read()).decode('utf-8'),
        'body_text': await response.text(),
        'body_json': await response.json()
      }

  @staticmethod
  async def batch(requests: list) -> list:
    """
    makes sync batch requests
  
    @param requests: (list) requests to make
    @returns: results of requests
    """
    results = []
    for request in requests:
      res = await Api.call(**request)
      results.append(res)
    return results

  @staticmethod
  async def batch_async(requests: list) -> list:
    """
    makes async batch requests
  
    @param requests: (list) requests to make
    @returns results of requests
    """
    coroutines = []
    for request in requests:
      coroutines.append(Api.call(**request))
    return await Async.all(coroutines)
