from cerberus import Validator

insights_schema = {
  '_id': {
    'type': 'string'
  },
  'method': {
    'type': 'string',
  },
  'service_id': {
    'type': 'string'
  },
  'path': {
    'type': 'string'
  },
  'remote_ip': {
    'type': 'string'
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
