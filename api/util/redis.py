import json
from bson import json_util
from api.util import Bson, DB
import base64

class Redis:
    
    @staticmethod
    async def fetch_members(set, db):
        keys = await db.smembers(set)
        results = []
        for key in keys:
            key_ = Bson.to_json(key)['$binary']
            val = await db.get(base64.b64decode(key_))
            if val is None:
                db.srem(set, base64.b64decode(key_))
                continue
            val_ = json.loads(base64.b64decode(Bson.to_json(val)['$binary']))
            results.append(val_)
        return results

    @staticmethod
    async def format_response(response):
        response = Bson.to_json(response)
        values = []
        for item in response:
            values.append(item)
        return values
