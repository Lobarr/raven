from cerberus import Validator

circuitBreaker_schema = {
  '_id': {
    'type': 'string'
  },
  'status': {
    'type': 'string',
    'allowed': ['BROKEN', 'ON', 'OFF']
  },
  'service_id': {
    'type': 'string'
  },
  'cooldown': {
    'type': 'integer'
  },
  'status_code': {
    'type': 'integer'
  },
  'method': {
    'type': 'string'
  },
  'path': {
    'type': 'string'
  },
  'threshold_percent': {
    'type': 'float',
    'min': '0.0',
    'max': '1.0'
  },
  'period': {
    'type': 'integer'
  },
  'tripped_count': {
    'type': 'integer'
  }
}

circuitBreaker_validator = Validator(circuitBreaker_schema)
