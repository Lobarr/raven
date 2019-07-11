from cerberus import Validator

service_schema = {
  '_id': {
    'type': 'string'
  },
  'name': {
    'type': 'string',
  },
  'state': {
    'type': 'string'
  },
  'target_list': {
    'type': 'list'
  },
  'current_target': {
    'type': 'string'
  },
  'whitelisted_clients': {
    'type': 'list'
  },
  'blacklisted_clients': {
    'type': 'list'
  },
  'public_key': {
    'type': 'string'
  }
}

service_validator = Validator(service_schema)
