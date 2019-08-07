from cerberus import Validator
from api.util import Bson

endpoint_cacher_schema = {\
  '_id': {
    'type': 'string'
  },
  'service_id': {
    'type': 'string', 
    'check_with': Bson.validate_schema_id
  },
  'endpoint': {
    'type': 'string',
  },
  'timeout': {
    'type': 'integer',
    'min': 0
  },
  'response_codes': {
    'type': 'list'
  }
}

enpoint_cacher_validator = Validator(endpoint_cacher_schema)
