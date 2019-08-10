from cerberus import Validator
from api.util import Bson

insights_schema = {
  '_id': {
    'type': 'string'
  },
  'method': {
    'type': 'string',
    'allowed': ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATH']
  },
  'service_id': {
    'type': 'string',
    'check_with': Bson.validate_schema_id
  },
  'path': {
    'type': 'string'
  },
  'remote_ip': {
    'type': 'string',
    'regex': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
  },
  'scheme': {
    'type': 'string',
    'allowed': ['http', 'https', 'ws']
  },
  'status_code': {
    'type': 'integer'
  },
  'content_types': {
    'type': 'list'
  },
  'elapsed_time': {
    'type': 'integer'
  }
}

insights_validator = Validator(insights_schema)
