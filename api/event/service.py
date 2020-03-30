import bson
import requests
from typing import List
from pydash import has
from cerberus import Validator
from aiohttp.client import ClientSession
from api.event import event_schema, EventDTO
from api.util import Validate, Api
from api.circuit_breaker import CircuitBreaker
from api.providers import DBProvider


collection_name = 'event'


class Event:
    @staticmethod
    async def create(event: EventDTO, db_provider: DBProvider):
        """
        creates an event

        @param ctx: (dict) event to create
        @param event_db: mongo collection instance
        @param circuit_breaker_db: mongo collection instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        
        if event.circuit_breaker_id:
            await CircuitBreaker.check_exists(event.circuit_breaker_id, db_provider)
        await db.insert_one(event.to_dict())

    @staticmethod
    async def update(event: EventDTO, db_provider: DBProvider):
        """
        updates an event

        @param id: (str) id of event
        @param ctx: (dict) fields to update
        @param db: mongo collection instance
        """
        db = db_provider.get_mongo_collection(collection_name)

        await db.update_one({'_id': bson.ObjectId(event.id)}, {'$set': event.to_dict()})

    @staticmethod
    async def get_by_id(_id: str, db_provider: DBProvider):
        """
        gets event by id

        @param id: (str) id to get event by
        @param db: mongo collection instance
        """
        db = db_provider.get_mongo_collection(collection_name)

        event_ctx = await db.find_one({'_id': bson.ObjectId(_id)})

        return Event.make_dto(event_ctx)

    @staticmethod
    async def get_by_circuit_breaker_id(_id: str, db_provider: DBProvider):
        """
        gets event by circuit breaker id

        @param id: (str) circuit breaker id to get event by
        @param db: mongo collection instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        cursor = db.find({'circuit_breaker_id': _id})
        event_contexts = await cursor.to_list(100)

        return [Event.make_dto(event_context) for event_context in event_contexts]

    @staticmethod
    async def get_by_target(target: str, db_provider: DBProvider):
        """
        gets event by target

        @param target: (str) target to get event by
        @param db: mongo collection instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        cursor = db.find({'target': target})
        event_contexts = await cursor.to_list(100)

        return [Event.make_dto(event_context) for event_context in event_contexts]

    @staticmethod
    async def get_all(db_provider: DBProvider) -> List[EventDTO]:
        """
        gets all events

        @param db: mongo collection instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        cursor = db.find({})
        event_contexts = await cursor.to_list(100)

        return [Event.make_dto(event_context) for event_context in event_contexts]

    @staticmethod
    async def remove(_id: str, db_provider: DBProvider):
        """
        removes event

        @param id: (str) id of event
        @param db: mongo collection instance

        """
        db = db_provider.get_mongo_collection(collection_name)
        
        await db.delete_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def handle_event(event: EventDTO):
        """
        handles event

        @param ctx: (EventDTO) body of event to handle
        """

        try:
            await Api.call(
                method='post',
                url=event.target,
                data=event.body,
                headers=event.headers
            )
        except:
            # TODO send email to admins on failure
            print('Mock send email')

    @staticmethod
    def make_dto(ctx: dict) -> EventDTO:
        event = EventDTO()
        
        if has(ctx, 'id') or has(ctx, '_id'):
            event.id = ctx['_id'] if '_id' in ctx else ctx['id']

        if has(ctx, 'circuit_breaker_id'):
            event.circuit_breaker_id = ctx['circuit_breaker_Id']

        if has(ctx, 'target'):
            event.target = ctx['target']

        if has(ctx, 'body'):
            event.body = ctx['body']

        if has(ctx, 'headers'):
            event.headers = ctx['headers']

        return event

