import pytest 
import asyncio
import asynctest
import mock
from cerberus import Validator
from password_strength import PasswordPolicy, PasswordStats
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys
from api.service import Service
from api.request_validator import RequestValidator, request_validator
from api.util import Validate, Crypt

class TestRequestValidator:
  @pytest.mark.asyncio
  async def test_create(self, *args):
    with asynctest.patch.object(Service, 'check_exists') as check_exists_mock:
      mock_ctx = {}
      mock_db = MagicMock()
      mock_db.insert_one = CoroutineMock()
      await RequestValidator.create(mock_ctx, mock_db)
      mock_db.insert_one.assert_awaited_with(mock_ctx)

      mock_ctx = {
        'service_id': 'some-value'
      }
      await RequestValidator.create(mock_ctx, mock_db)
      check_exists_mock.assert_called()



  @pytest.mark.asyncio
  async def test_update(self, *args):
    with patch('bson.ObjectId') as bson_object_id_mock:
      mock_id = 'some-value'
      bson_object_id_mock.return_value = mock_id  
      mock_ctx = {}
      mock_db = MagicMock()
      mock_db.update_one = CoroutineMock()

      await RequestValidator.update(mock_id, mock_ctx, mock_db)
      mock_db.update_one.assert_called()
      bson_object_id_mock.assert_called_with(mock_id)
      expect(mock_db.update_one.await_args[0][0]['_id']).to(equal(mock_id))
  
  @pytest.mark.asyncio
  async def test_delete(self, *args):
    with patch('bson.ObjectId') as object_id_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.delete_one = CoroutineMock()
      await RequestValidator.delete(mock_id, mock_db)
      mock_db.delete_one.assert_called()
      object_id_mock.assert_called_with(mock_id)

  @pytest.mark.asyncio
  async def test_get_all(self, *args):
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await RequestValidator.get_all(mock_db)
    mock_db.find.assert_called_with({})
    mock_cursor.to_list.assert_called()
  
  @pytest.mark.asyncio
  async def test_get_by_service_id(self, *args):
    mock_service_id = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await RequestValidator.get_by_service_id(mock_service_id, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'service_id': mock_service_id})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_method(self, *args):
    mock_method = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await RequestValidator.get_by_method(mock_method, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'method': mock_method})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_endpoint(self, *args):
    mock_endpoint = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await RequestValidator.get_by_endpoint(mock_endpoint, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'endpoint': mock_endpoint})
    mock_cursor.to_list.assert_called()
  
  @pytest.mark.asyncio
  async def test_validate_schema(self, *args):
    with patch.object(Validator, 'validate') as validator_mock:
      mock_request_body = {}
      mock_schema = {}
      await RequestValidator.validate_schema(mock_request_body, mock_schema)
      validator_mock.assert_called_with(mock_schema)
      validator_mock.assert_called_with(mock_request_body)

      try:
        validator_mock.validate.return_value = False
        await RequestValidator.validate_schema(mock_request_body, mock_schema)
      except Exception as err:
        expect(err.args[0]).to(have_keys('message', 'status_code'))
  
  @pytest.mark.asyncio
  async def test_enforce_policy(self, *args):
    with patch.object(PasswordPolicy, 'from_names') as from_names_mock:
      password_policy_mock = MagicMock()
      password_policy_mock.test.return_value = []
      from_names_mock.return_value = password_policy_mock
      mock_password = 'some-value'
      mock_policy = {
        'length': 'some-value',
        'upper_case_count': 'some-value',
        'numbers_count': 'some-value',
        'specials_count': 'some-value',
        'non_letters_count': 'some-value'
      }
      await RequestValidator.enforce_policy(mock_password, mock_policy)
      from_names_mock.assert_called_with(
        length=mock_policy['length'],
        uppercase=mock_policy['upper_case_count'],
        numbers=mock_policy['numbers_count'],
        special=mock_policy['specials_count'],
        nonletters=mock_policy['non_letters_count'],
      )
      password_policy_mock.test.assert_called_with(mock_password)

      try:
        password_policy_mock.test.return_value = [None]
        await RequestValidator.enforce_policy(mock_password, mock_policy)
      except Exception as err:
        expect(err.args[0]).to(have_keys('message', 'status_code'))
      
  @pytest.mark.asyncio
  async def test_enforce_strength(self, *args):
    with patch('password_strength.PasswordStats.strength') as password_stats_mock:
      password_stats_mock.return_value = 1.00
      mock_password = 'some-value'
      mock_strength_percentage = 0.90
      await RequestValidator.enforce_strength(mock_password, mock_strength_percentage)

  @pytest.mark.asyncio
  async def test_get_by_id(self, *args):
    with patch('bson.ObjectId') as bson_object_id_mock:
      mock_id = 'some-value'
      bson_object_id_mock.return_value = mock_id  
      mock_db = MagicMock()
      mock_db.find_one = CoroutineMock()

      await RequestValidator.get_by_id(mock_id, mock_db)
      mock_db.find_one.assert_called()
      bson_object_id_mock.assert_called_with(mock_id)
      expect(mock_db.find_one.await_args[0][0]['_id']).to(equal(mock_id))
