from expects import expect, have_keys, equal
from api.request_validator import request_validator_schema

def test_request_validator_schema():
  expect(request_validator_schema).to(have_keys('_id', 'service_id', 'method', 'endpoint', 'schema', 'password_field', 'password_policy', 'err_response_code'))

  for prop in ['_id', 'service_id','method', 'endpoint', 'password_field']:
    expect(request_validator_schema[prop]['type']).to(equal('string'))
  
  for prop in ['schema', 'password_policy']:
    expect(request_validator_schema[prop]['type']).to(equal('dict'))
  
  for prop in ['err_response_code']:
    expect(request_validator_schema[prop]['type']).to(equal('integer'))
  
  for prop in ['length', 'upper_case_count', 'numbers_count', 'specials_count', 'non_letters_count', ]:
    expect(request_validator_schema['password_policy']['schema'][prop]['type']).to(equal('integer'))

  for prop in ['strength_percentage']:
    expect(request_validator_schema['password_policy']['schema'][prop]['type']).to(equal('float'))
