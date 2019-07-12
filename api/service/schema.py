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
  'secure': {
    'type': 'boolean'
  },
  'targets': {
    'type': 'list'
  },
  'target': {
    'type': 'string'
  },
  'whitelisted_hosts': {
    'type': 'list'
  },
  'blacklisted_hosts': {
    'type': 'list'
  },
  'public_key': {
    'type': 'string'
  }
}

service_validator = Validator(service_schema)
