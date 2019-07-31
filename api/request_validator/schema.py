from cerberus import Validator

request_validator_schema = {
  '_id': {
    'type': 'string',
  },
  'service_id': {
    'type': 'string',
  },
  'method': {
    'type': 'string',
  },
  'endpoint': {
    'type': 'string',
  },
  'schema': {
    'type': 'dict',
  },
  'password_field': {
    'type': 'string',
  },
  'password_policy': {
    'type': 'dict',
    'schema': {
        'length': {
            'type': 'integer',
        },
        'upper_case_count': {
            'type': 'integer',
        },
        'numbers_count': {
            'type': 'integer',
        },
        'specials_count': {
            'type': 'integer',
        },
        'non_letters_count': {
            'type': 'integer',
        }, 
        'strength': {
          'type': 'float',
          'min': '0.0',
          'max': '1.0'
        }
    }
  },
  'err_response_code': {
    'type': 'integer',
  }
}

request_validator = Validator(request_validator_schema)
