
import asyncio
from celery import Celery
from api.util.env import REDIS
from api.event import Event

app = Celery('tasks', broker=REDIS)

@app.task
def handle_event(ctx: object):
  asyncio.run(Event.handle_event(ctx))
