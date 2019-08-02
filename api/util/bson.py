import json
import bson
from bson import json_util

class Bson:
  @staticmethod
  def to_json(ctx):
    return json.loads(json_util.dumps(ctx))

  @staticmethod
  def validate_schema_id(field, value, error):
    if not bson.ObjectId.is_valid(value):
      error(field, 'Must be a bson object id')
