from cerberus import Validator

requestvalidator_schema = {
  'objectId': {
    'type': 'string',
    'required': True
  },
  'serviceId': {
    'type': 'string',
    'required': True
  },
  'method': {
    'type': 'string',
    'required': True
  },
  'path': {
    'type': 'string',
    'required': True
  },
  'schema': {
    'type': 'dict',
    'required': True
  },
  'passwordField': {
    'type': 'string',
    'required': True
  },
  'password_policy': {
    'type': 'dict',
    'required': True,
    'schema': {
        'length': {
            'type': 'integer',
            'required': True
        },
        'upperCaseCount': {
            'type': 'integer',
            'required': True
        },
        'numbersCount': {
            'type': 'integer',
            'required': True
        },
        'specialCount': {
            'type': 'integer',
            'required': True
        },
        'nonLettersCount': {
            'type': 'integer',
            'required': True
        }
    }
  },
  'errResponseCode': {
    'type': 'integer',
    'required': True
  }
}

request_validator = Validator(requestvalidator_schema)
