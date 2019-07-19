
import asyncio
from celery import Celery
from api.util.env import REDIS
from api.event import Event

tasks = Celery('tasks', broker=REDIS)

@tasks.task
def handle_event(ctx: object):
  asyncio.run(Event.handle_event(ctx))

@tasks.task
def add(a,b):
  return a+b
