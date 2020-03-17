from expects import expect, have_keys, equal
from api.circuit_breaker import circuit_breaker_schema


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
