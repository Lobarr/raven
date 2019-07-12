from cerberus import Validator

event_schema = {
  '_id': {
    'type': 'string'
  },
  'circuit_breaker_id': {
    'type': 'string'
  },
  # 'events': {
  #   'type': 'list',
  # }
}

event_validator = Validator(event_schema)
