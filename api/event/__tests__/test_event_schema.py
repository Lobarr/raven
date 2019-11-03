from expects import expect, have_keys, equal
from api.event import event_schema


def test_event_schema():
    expect(event_schema).to(
        have_keys('_id', 'circuit_breaker_id', 'target', 'body', 'headers'))
    for prop in ['_id', 'circuit_breaker_id', 'target']:
        expect(event_schema[prop]['type']).to(equal('string'))

    for prop in ['body', 'headers']:
        expect(event_schema[prop]['type']).to(equal('dict'))
