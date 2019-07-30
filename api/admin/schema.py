from cerberus import Validator

admin_schema = {
	'_id': {
	  'type': 'string'
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
admin_validator = Validator(admin_schema)
