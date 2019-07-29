from cerberus import Validator

circuit_breaker_schema = {
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

circuit_breaker_validator = Validator(circuit_breaker_schema)
