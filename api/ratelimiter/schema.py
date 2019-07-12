from cerberus import Validator

ratelimit_rule_schema = {
    'objectId': {
        'type': 'string',
        'required': True
    },
    'path': {
        'type': 'string',
        'required': True
    },
    'maxRequests': {
        'type': 'integer',
        'required': True
    },
    'timeLimit': {
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
    'statusCode': {
        'type': 'integer',
        'required': True
    }
}

ratelimit_entry_schema = {
    'ruleId': {
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

ratelimit_rule_validator = Validator(ratelimit_rule_schema)
ratelimit_entry_validator = Validator(ratelimit_entry_schema)