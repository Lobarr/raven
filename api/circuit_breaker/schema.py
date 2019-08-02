from cerberus import Validator
from api.util  import Bson

circuit_breaker_schema = {
  '_id': {
    'type': 'string'
  },
  'status': {
    'type': 'string',
    'allowed': ['BROKEN', 'ON', 'OFF']
  },
  'service_id': {
    'type': 'string',
    'check_with': Bson.validate_schema_id
  },
  'cooldown': {
    'type': 'integer',
    'min': 0
  },
  'status_code': {
    'type': 'integer'
  },
  'method': {
    'type': 'string',
    'allowed': ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATH']
  },
  'path': {
    'type': 'string'
  },
  'threshold': {
    'type': 'float',
    'min': 0.0,
    'max': 1.0
  },
  'period': {
    'type': 'integer',
    'min': 0,
    'default': 60
  },
  'tripped_count': {
    'type': 'integer',
    'default': 0
  }
}

circuit_breaker_validator = Validator(circuit_breaker_schema)
