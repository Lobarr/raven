
import asyncio
import aioredis
import pydash
import logging
from celery import Celery, Task
from motor.motor_asyncio import AsyncIOMotorClient
from api.util.env import REDIS, DB
from api.event import Event
from api.util import Api
from api.admin import Admin

tasks = Celery('api.util.tasks', broker=REDIS)

class Provider(Task):
  _mongo = None
  _redis = None
  _loop = None
  _funcs = {
    'admin.count': Admin.count,
    'print': print
  }

  @property
  def mongo(self):
      if self._mongo is None:
          self._mongo = AsyncIOMotorClient(DB).raven
      return self._mongo
  
  @property
  def redis(self):
    if self._redis is None:
      self._redis = self.loop.run_until_complete(aioredis.create_redis(REDIS))
    return self._redis

  @property
  def loop(self):
    if self._loop is None:
      self._loop = asyncio.get_event_loop()
    return self._loop

@tasks.task(base=Provider, name='raven.api.task.async')
def handle_task_async(func, *args):
  """
  handles async task

  supports ability to pass mongo and redis as params
  mongo: "mongo:collection_name"
  redis: "redis"
  """
  _args = list(args)
  for index, arg in enumerate(_args):
    if 'mongo' in arg:
      collection = arg.split(':')[1]
      _args[index] = handle_task_async.mongo[collection]
    elif 'redis' in arg:
      _args[index] = handle_task_async.redis
  if func in handle_task_async._funcs:
    new_args = tuple(_args)
    return handle_task_async.loop.run_until_complete(handle_task_async._funcs[func](*new_args))

@tasks.task(base=Provider, name='raven.api.task.sync')
def handle_task_sync(func, *args):
  """
  handles sync task
  """
  if func in handle_task_sync._funcs:
    return handle_task_sync._funcs[func](*args)
