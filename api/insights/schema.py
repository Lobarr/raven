from cerberus import Validator

insights_schema = {
  '_id': {
    'type': 'string'
  },
  'method': {
    'type': 'string',
    'allowed': ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATH']
  },
  'service_id': {
    'type': 'string'
  },
  'path': {
    'type': 'string'
  },
  'remote_ip': {
    'type': 'string',
    'regex': r'^{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
  },
  'scheme': {
    'type': 'string',
    'allowed': ['http', 'https', 'ws']
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
