from expects import expect, have_keys, equal
from api.circuit_breaker.schema import circuit_breaker_schema, CircuitBreakerStatus
from api.circuit_breaker.service import CircuitBreaker


def test_circuit_breaker_schema():
    expect(circuit_breaker_schema).to(
        have_keys(
            '_id',
            'status',
            'service_id',
            'cooldown',
            'status_codes',
            'method',
            'threshold',
        )
    )

    for prop in ['_id', 'status', 'service_id', 'method']:
        expect(circuit_breaker_schema[prop]['type']).to(equal('string'))

    for prop in ['cooldown', 'period', 'tripped_count']:
        expect(circuit_breaker_schema[prop]['type']).to(equal('integer'))

    for prop in ['threshold']:
        expect(circuit_breaker_schema[prop]['type']).to(equal('float'))

    for prop in ['status_codes']:
        expect(circuit_breaker_schema[prop]['type']).to(equal('list'))

class TestCiruitCreakerDTO:
  def test_to_dict(self, *args):
    circuit_breaker_ctx = {
        'id': 'some-id',
        'status': CircuitBreakerStatus.OFF.name,
        'service_id': 'some-id',
        'cooldown': 1,
        'status_codes': [200,400],
        'method': 'GET',
        'threshold': 0.2,
        'period': 60,
        'tripped_count': 5,
    }
    circuit_breaker = CircuitBreaker.make_dto(circuit_breaker_ctx)
    circuit_breaker_dict = circuit_breaker.to_dict()

    expect(circuit_breaker_dict).not_to(have_keys('_CircuitBreakerDTO__schema', '_CircuitBreakerDTO__validator', 'id'))
    expect(circuit_breaker_dict).to(have_keys('status', '_id', 'service_id', 'cooldown', 'status_codes', 'method', 'threshold', 'period', 'tripped_count'))
