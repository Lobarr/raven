
import asyncio
import aioredis
import pydash
import logging
from celery import Celery, Task
from celery.schedules import crontab
from motor.motor_asyncio import AsyncIOMotorClient
from api.util.env import REDIS, DB
from api.event import Event
from api.util import Api
from api.admin import Admin
from api.service import Service
from api.circuit_breaker import CircuitBreaker
from api.endpoint_cacher import EndpointCacher
from api.insights import Insights
from api.rate_limiter import RateLimiter

tasks = Celery('api.util.tasks', broker=REDIS, backend=REDIS)

tasks.conf.beat_schedule = {
  'raven.api.rate_limiter.clear_empty_entries': {
    'task': 'raven.api.task.async',
    'schedule': crontab(), 
    'args': [{
      'func': 'RateLimiter.clear_empty_entries',
      'args': ['redis'],
      'kwargs': {}
    }]
  }
}

class TaskProvider(Task):
  _mongo = None
  _redis = None
  _loop = None
  _funcs = {
    'Admin.count': Admin.count,
    'Api.call': Api.call,
    'CircuitBreaker.incr_count': CircuitBreaker.incr_count,
    'CircuitBreaker.incr_tripped_count': CircuitBreaker.incr_tripped_count,
    'CircuitBreaker.set_queued': CircuitBreaker.set_queued,
    'CircuitBreaker.update': CircuitBreaker.update,
    'EndpointCacher.set_cache': EndpointCacher.set_cache,
    'Event.handle_event': Event.handle_event,
    'Insights.create': Insights.create,
    'RateLimiter.clear_empty_entries': RateLimiter.clear_empty_entries,
    'RateLimiter.create_entry': RateLimiter.create_entry,
    'RateLimiter.increment_entry_count': RateLimiter.increment_entry_count,
    'RateLimiter.update_entry': RateLimiter.update_entry,
    'Service.advance_target': Service.advance_target,
    'Service.update': Service.update
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

@tasks.task(base=TaskProvider, name='raven.api.task.async')
def handle_task_async(ctx: dict):
  """
  handles async task

  supports ability to pass mongo and redis as params
  mongo: "mongo:collection_name"
  redis: "redis"
  """
  _args = ctx['args']
  for index, arg in enumerate(_args):
    if pydash.is_string(arg) and 'mongo' in arg:
      collection = arg.split(':')[1]
      _args[index] = handle_task_async.mongo[collection]
    elif pydash.is_string(arg) and 'redis' in arg:
      _args[index] = handle_task_async.redis
  if ctx['func'] in handle_task_async._funcs:
    new_args = tuple(_args)
    return handle_task_async.loop.run_until_complete(handle_task_async._funcs[ctx['func']](*new_args, **ctx['kwargs']))

@tasks.task(base=TaskProvider, name='raven.api.task.sync')
def handle_task_sync(ctx):
  """
  handles sync task
  """
  if ctx['func'] in handle_task_sync._funcs:
    return handle_task_sync._funcs[ctx['func']](*ctx['args'], **ctx['kwargs'])
