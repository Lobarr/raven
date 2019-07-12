from cerberus import Validator

authservice_schema = {
  '_id': {
    'type': 'string'
  },
  'current_target': {
    'type': 'string',
  },
  'targets': {
    'type': 'list'
  },
  'headers': {
    'type': 'dict'
  },
  'body': {
    'type': 'dict'
  }
}

authservice_validator = Validator(authservice_schema)
