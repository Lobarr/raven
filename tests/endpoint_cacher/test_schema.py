from expects import expect, have_keys, equal
from api.endpoint_cacher import endpoint_cache_schema

def test_endpoint_cache_schema():
  expect(endpoint_cache_schema).to(have_keys('_id', 'service_id', 'timeout', 'response_codes'))
  for prop in ['_id', 'service_id']:
    expect(endpoint_cache_schema[prop]['type']).to(equal('string'))

  for prop in ['timeout']:
    expect(endpoint_cache_schema[prop]['type']).to(equal('integer'))
  
  for prop in ['response_codes']:
    expect(endpoint_cache_schema[prop]['type']).to(equal('list'))
