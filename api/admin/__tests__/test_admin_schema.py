from mock import patch
from expects import expect, have_keys, equal, have_keys
from api.admin import admin_schema, Admin
from api.util import Hasher


def test_admin_schema():
  expect(admin_schema).to(
    have_keys('_id', 'email', 'username', 'password', 'token'))
  for prop in ['_id', 'email', 'username', 'password', 'token']:
    expect(admin_schema[prop]['type']).to(equal('string'))

class TestAdminDTO:
  def test_to_dict(self, *args):
    admin_ctx = {
      'email': 'some-email',
      'id': 'some-id',
      'password': 'some-password',
      'token': 'some-token',
      'username': 'some-username',
    }
    admin = Admin.make_dto(admin_ctx)
    admin_dict = admin.to_dict()

    expect(admin_dict).not_to(have_keys('_AdminDTO__schema', '_AdminDTO__validator', 'id'))
    expect(admin_dict).to(have_keys('email', '_id', 'password', 'token', 'username'))

  @patch.object(Hasher, 'hash')
  def test_hash_password(self, *args):
    admin_ctx = {
      'email': 'some-email',
      'id': 'some-id',
      'password': 'some-password',
      'token': 'some-token',
      'username': 'some-username',
    }
    admin = Admin.make_dto(admin_ctx)
    mock_hashed_password = 'hashed-password'
    args[0].return_value = mock_hashed_password

    admin.hash_password()

    args[0].assert_called_with(admin_ctx['password'])
    expect(admin.password).to(equal(mock_hashed_password))

  