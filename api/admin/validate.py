from api.util import Bson

admin_schema = {
    '_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'email': {
        'type': 'string',
        'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    },
    'username': {
        'type': 'string'
    },
    'password': {
        'type': 'string'
    },
    'token': {
        'type': 'string'
    }
}

