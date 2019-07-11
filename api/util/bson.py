import json
from bson import json_util

class Bson:
  @staticmethod
  def to_json(ctx):
    return json.loads(json_util.dumps(ctx))
