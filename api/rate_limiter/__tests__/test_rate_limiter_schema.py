from expects import expect, have_keys, equal
from api.rate_limiter import rate_limit_entry_schema, rate_limit_rule_schema

def test_rate_limit_entry_schema():
  expect(rate_limit_entry_schema).to(have_keys('_id', 'rule_id', 'host', 'count'))
  for prop in ['_id', 'rule_id', 'host']:
    expect(rate_limit_entry_schema[prop]['type']).to(equal('string'))
  
  for prop in ['count']:
    expect(rate_limit_entry_schema[prop]['type']).to(equal('integer'))

def test_rate_limit_rule_schema():
  expect(rate_limit_rule_schema).to(have_keys('_id', 'max_requests', 'timeout', 'message', 'status_code', 'service_id'))
  for prop in ['_id', 'message']:
    expect(rate_limit_rule_schema[prop]['type']).to(equal('string'))
  
  for prop in ['max_requests', 'timeout', 'status_code']:
    expect(rate_limit_rule_schema[prop]['type']).to(equal('integer'))
