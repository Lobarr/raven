from expects import expect, have_keys, equal
from api.service import service_schema

def test_service_schema():
  expect(service_schema).to(have_keys('_id', 'name', 'state', 'secure', 'targets', 'target', 'whitelisted_hosts', 'blacklisted_hosts', 'public_key'))
  for prop in ['_id', 'name', 'state', 'target', 'public_key']:
    expect(service_schema[prop]['type']).to(equal('string'))

  for prop in ['secure']:
    expect(service_schema[prop]['type']).to(equal('boolean'))

  for prop in ['targets', 'whitelisted_hosts', 'blacklisted_hosts']:
    expect(service_schema[prop]['type']).to(equal('list'))
