from expects import expect, have_keys, equal
from api.admin import admin_schema


def test_admin_schema():
    expect(admin_schema).to(
        have_keys('_id', 'email', 'username', 'password', 'token'))
    for prop in ['_id', 'email', 'username', 'password', 'token']:
        expect(admin_schema[prop]['type']).to(equal('string'))
