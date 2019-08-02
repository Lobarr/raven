from cerberus import Validator

service_schema = {
  '_id': {
    'type': 'string'
  },
  'name': {
    'type': 'string',
  },
  'state': {
    'type': 'string',
    'allowed': ['DOWN', 'UP', 'OFF'],
    'default': 'OFF'
  },
  'secure': {
    'type': 'boolean',
    'default': False
  },
  'targets': {
    'type': 'list',
    'default': []
  },
  'cur_target_index': {
    'type': 'integer',
    'default': 0,
    'dependencies': 'targets'
  },
  'whitelisted_hosts': {
    'type': 'list',
    'default': []
  },
  'blacklisted_hosts': {
    'type': 'list',
    'default': []
  },
  'public_key': {
    'type': 'string'
  }
}

service_validator = Validator(service_schema)
