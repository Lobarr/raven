import bson

class Validate:
  @staticmethod
  def object_id(id: str):
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'message': 'Invalid id provided',
        'status_code': 400
      })
  
  @staticmethod
  def schema(ctx, schema):
    if not schema.validate(ctx):
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400
      })
