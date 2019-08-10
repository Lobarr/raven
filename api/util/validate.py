import bson
from cerberus import Validator

class Validate:
  @staticmethod
  def object_id(id: str):
    """
    validates a bson object id
  
    @param id: (str) id to be validated
    """
    if bson.ObjectId.is_valid(id) != True:
      raise Exception({
        'message': 'Invalid id provided',
        'status_code': 400
      })
  

  @staticmethod
  def schema(ctx: object, validator: Validator):
    """
    validates a given object with given validator
  
    @param ctx: (object) object to be validated
    @param validator: (Validator) validator to validate schema with
    """
    if not validator.validate(ctx):
      raise Exception({
        'message': 'Invalid data provided',
        'status_code': 400,
        'errors': validator.errors
      })
