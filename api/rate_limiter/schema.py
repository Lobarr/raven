from cerberus import Validator

rate_limit_rule_schema = {
    '_id': {
        'type': 'string',
        'required': True
    },
    'path': {
        'type': 'string',
        'required': True
    },
    'max_requests': {
        'type': 'integer',
        'required': True
    },
    'time_limit': {
        'type': 'integer',
        'required': True
    },
    'host': {
        'type': 'string',
        'required': True
    },
    'message': {
        'type': 'string',
        'required': True
    },
    'status_code': {
        'type': 'integer',
        'required': True
    }
}

rate_limit_entry_schema = {
    'rule_id': {
        'type': 'string',
        'required': True
    },
    'host': {
        'type': 'string',
        'required': True
    },
    'count': {
        'type': 'integer',
        'required': True
    }
}

rate_limit_rule_validator = Validator(rate_limit_rule_schema)
rate_limit_entry_validator = Validator(rate_limit_entry_schema)
