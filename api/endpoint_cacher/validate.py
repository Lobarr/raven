from cerberus import Validator
from api.util import Bson

endpoint_cacher_schema = {
    '_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'service_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'timeout': {
        'type': 'integer',
        'min': 0
    },
    'response_codes': {
        'type': 'list'
    }
}
