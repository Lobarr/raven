from expects import expect, have_keys, equal
from api.insights import insights_schema


def test_insights_schema():
    expect(insights_schema).to(
        have_keys(
            '_id',
            'method',
            'service_id',
            'path',
            'remote_ip',
            'scheme',
            'status_code',
            'content_type',
            'elapsed_time'))

    for prop in ['_id', 'service_id', 'method', 'path', 'remote_ip', 'scheme']:
        expect(insights_schema[prop]['type']).to(equal('string'))

    for prop in ['content_type']:
        expect(insights_schema[prop]['type']).to(equal('string'))

    for prop in ['status_code', 'elapsed_time']:
        expect(insights_schema[prop]['type']).to(equal('integer'))
