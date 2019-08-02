from expects import expect, have_keys, equal
from api.circuit_breaker import circuit_breaker_schema

def test_circuit_breaker_schema():
  expect(circuit_breaker_schema).to(have_keys('_id', 'status', 'service_id', 'cooldown', 'status_code', 'method', 'path', 'threshold'))
  for prop in ['_id', 'status', 'service_id', 'method', 'path']:
    expect(circuit_breaker_schema[prop]['type']).to(equal('string'))

  for prop in ['cooldown', 'status_code', 'period', 'tripped_count']:
    expect(circuit_breaker_schema[prop]['type']).to(equal('integer'))

  for prop in ['threshold']:
    expect(circuit_breaker_schema[prop]['type']).to(equal('float'))