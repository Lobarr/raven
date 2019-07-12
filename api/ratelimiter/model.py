import asyncio
import aioredis
import bson
import json
import base64
from motor.motor_asyncio import AsyncIOMotorClient
from cerberus import Validator
from api.ratelimiter.schema import ratelimit_rule_schema, ratelimit_rule_validator, ratelimit_entry_schema, ratelimit_entry_validator
from api.util import Bson, Redis

class RateLimiter:
    
    @staticmethod
    async def create_rule(ctx, db):
        """
        Creates a rate limiter rule.

        @param ctx: (object) data to be inserted
        @param db: (object) db connection
        """
        ctx['objectId'] = str(bson.ObjectId())
        if ratelimit_rule_validator.validate(ctx) is True:
            await db.set(ctx['objectId'], json.dumps(ctx))
            await db.sadd('ratelimit_rules', ctx['objectId'])
        else:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
            
    @staticmethod
    async def update_rule(id, ctx, db):
        """
        Updates a rate limiter rule.

        @param ctx: (object) data to use for update
        @param db: (object) db connection
        """
        ctx['objectId'] = id
        if ratelimit_rule_validator.validate(ctx) is True and bson.ObjectId.is_valid(id):
            await db.set(id, json.dumps(ctx))
        else:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
            
    @staticmethod
    async def delete_rule(id, db):
        """
        Deletes a rate limiter rule.

        @param id: (string) the ID of the rate limiter rule to delete
        @param db: (object) db connection
        """
        if bson.ObjectId.is_valid(id) != True:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
        await db.delete(id)
        await db.srem('ratelimit_rules', id)

    @staticmethod
    async def get_rules_by_status_code(statusCode, db):
        """
        Gets a rate limiter rule by the status code

        @param statusCode: (string) status code of the rate limiter rule
        @param db: (object) db connection
        @return: the records with the provided statusCode
        """
        results = await Redis.fetch_members('ratelimit_rules', db)
        results = [r for r in results if str(r['statusCode']) == statusCode]
        return results
            
    
    @staticmethod
    async def get_rules_by_path(path, db):
        """
        Gets a rate limiter rule by the path of the rule

        @param path: (string) path of the rate limiter rule
        @param db: (object) db connection
        @return: the records with the given path
        """
        results = await Redis.fetch_members('ratelimit_rules', db)
        results = [r for r in results if r['path'] == path]
        return results
    
    @staticmethod
    async def get_all_rules(db):
        """
        Gets a rate limiter rule by the status code

        @param statusCode: (string) status code of the rate limiter rule
        @param db: (object) db connection
        @return: the records with the provided statusCode
        """
        results = await Redis.fetch_members('ratelimit_rules', db)
        return results
            
    @staticmethod
    async def create_entry(ctx, db):
        """
        Creates a rate limiter entry.

        @param ctx: (object) data to be inserted
        @param db: (object) db connection
        """
        if ratelimit_entry_validator.validate(ctx) is True and bson.ObjectId.is_valid(ctx['ruleId']):
            await db.set(ctx['host'], json.dumps(ctx))
            await db.sadd('ratelimit_entries', ctx['host'])
            
            entry = await db.get(ctx['ruleId'])
            entry_data = json.loads(entry)
            await db.expire(ctx['host'], int(entry_data['timeLimit']))
        else:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
            
    @staticmethod
    async def update_entry(host, ctx, db):
        """
        Updates a rate limiter entry.

        @param ctx: (object) data to use for update
        @param db: (object) db connection
        """
        if ratelimit_entry_validator.validate(ctx) is True:
            await db.set(host, json.dumps(ctx))
        else:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
            
    @staticmethod
    async def delete_entry(host, db):
        """
        Deletes a rate limiter entry.

        @param host: (string) the hostname of the rate limiter entry to delete
        @param db: (object) db connection
        """
        await db.delete(host)
        await db.srem('ratelimit_entries', host)

    @staticmethod
    async def get_all_entries(db):
        """
        Gets all rate limiter entries
        
        @param db: (object) db connection
        @return: the records with the provided statusCode
        """
        results = await Redis.fetch_members('ratelimit_entries', db)
        return results
    
    @staticmethod
    async def increment_entry_count(id, db):
        entry = await db.get(id)
        entry_data = json.loads(entry)
        entry_data['count'] = entry_data['count'] + 1
        await db.set(id, json.dumps(entry_data))
        
    @staticmethod
    async def decrement_entry_count(id, db):
        entry = await db.get(id)
        entry_data = json.loads(entry)
        entry_data['count'] = entry_data['count'] - 1
        await db.set(id, json.dumps(entry_data))