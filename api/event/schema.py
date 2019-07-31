from cerberus import Validator

event_schema = {
  '_id': {
    'type': 'string'
  },
  'circuit_breaker_id': {
    'type': 'string'
  },
  'target': {
    'type': 'string'
  },
  'body': {
    'type': 'dict'
  },
  'headers': {
    'type': 'dict'
  }
}

event_validator = Validator(event_schema)
