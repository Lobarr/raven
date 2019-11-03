import pytest 
import asyncio
import mock
import asynctest
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys
from api.admin import Admin, admin_validator
from api.util import Validate, Crypt, Hasher

class TestAdmin:
  @pytest.mark.asyncio
  async def test_create(self, *args):
    with patch.object(Hasher, 'hash') as hash_mock:
      mock_ctx = {
        'password': 'some-value'
      }
      hash_mock.return_value = mock_ctx['password']
      mock_db = MagicMock()
      mock_db.insert_one = CoroutineMock()
      await Admin.create(mock_ctx, mock_db)
      mock_db.insert_one.assert_awaited_with(mock_ctx)
      hash_mock.assert_called_with(mock_ctx['password'])

  @pytest.mark.asyncio
  async def test_update(self, *args):
    with patch('bson.ObjectId') as bson_object_id_mock:
      with patch.object(Hasher, 'hash') as hash_mock:
        mock_id = 'some-value'
        bson_object_id_mock.return_value = mock_id  
        mock_ctx = {}
        mock_db = MagicMock()
        mock_db.update_one = CoroutineMock()

        await Admin.update(mock_id, mock_ctx, mock_db)
        mock_db.update_one.assert_called()
        bson_object_id_mock.assert_called_with(mock_id)
        expect(mock_db.update_one.await_args[0][0]['_id']).to(equal(mock_id))

        mock_ctx = {
          'password': 'some-value'
        }
        hash_mock.return_value = mock_ctx['password']
        await Admin.update(mock_id, mock_ctx, mock_db)
        hash_mock.assert_called_with(mock_ctx['password'])
  
  @pytest.mark.asyncio
  async def test_get_by_id(self, *args):
    with patch('bson.ObjectId') as object_id_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.find_one = CoroutineMock()
      object_id_mock.return_value = mock_id
      await Admin.get_by_id(mock_id, mock_db)
      object_id_mock.assert_called_with(mock_id)
      mock_db.find_one.assert_called()
      mock_db.find_one.assert_awaited_with({'_id': mock_id})
  
  @pytest.mark.asyncio
  async def test_remove(self, *args):
    with patch('bson.ObjectId') as object_id_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.delete_one = CoroutineMock()
      await Admin.remove(mock_id, mock_db)
      mock_db.delete_one.assert_called()
      object_id_mock.assert_called_with(mock_id)

  @pytest.mark.asyncio
  async def test_get_all(self, *args):
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await Admin.get_all(mock_db)
    mock_db.find.assert_called_with({})
    mock_cursor.to_list.assert_called()
  
  @pytest.mark.asyncio
  async def test_get_by_email(self, *args):
    mock_email = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await Admin.get_by_email(mock_email, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'email': mock_email})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_username(self, *args):
    mock_username = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await Admin.get_by_username(mock_username, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'username': mock_username})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_verify_password(self, *args):
    with asynctest.patch.object(Admin, 'get_by_username') as get_by_username_mock:
      with patch.object(Hasher, 'validate') as validate_mock:
        mock_username = 'some-value'
        mock_password = 'some-value'
        mock_db = MagicMock()
        mock_db.find = CoroutineMock()
        mock_admin = {
          'password': 'some-value'
        }
        get_by_username_mock.return_value = mock_admin
        await Admin.verify_password(mock_username, mock_password, mock_db)
        get_by_username_mock.assert_awaited_with(mock_username, mock_db)
        expect(validate_mock.call_args[0][0]).to(equal(mock_password))
        expect(validate_mock.call_args[0][1]).to(equal(mock_admin['password']))

  @pytest.mark.asyncio
  async def test_count(self, *args):
    mock_db = MagicMock()
    mock_db.count_documents = CoroutineMock()
    await Admin.count(mock_db)
    mock_db.count_documents.assert_awaited_with({})
  
  @pytest.mark.asyncio
  async def test_create_default(self, *args):
    with asynctest.patch.object(Admin, 'count') as count_mock:
      with asynctest.patch.object(Admin, 'create') as create_mock:
        count_mock.return_value = 1
        mock_db = CoroutineMock()
        await Admin.create_default(mock_db)
        count_mock.assert_called_with(mock_db)
        create_mock.assert_not_awaited()

        count_mock.return_value = 0
        await Admin.create_default(mock_db)
        create_mock.assert_called()
        expect(create_mock.call_args[0][0]).to(have_keys('username', 'password'))

