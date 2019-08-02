import pytest 
import asyncio
import mock
import asynctest
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys
from api.circuit_breaker import CircuitBreaker, circuit_breaker_validator
from api.util import Validate, Crypt

class TestCircuitBreaker:
  @pytest.mark.asyncio
  async def test_create(self, *args):
    mock_ctx = {}
    mock_db = MagicMock()
    mock_db.insert_one = CoroutineMock()
    await CircuitBreaker.create(mock_ctx, mock_db)
    mock_db.insert_one.assert_awaited_with(mock_ctx)

  @pytest.mark.asyncio
  async def test_update(self, *args):
    with patch('bson.ObjectId') as bson_object_id_mock:
      mock_id = 'some-value'
      bson_object_id_mock.return_value = mock_id  
      mock_ctx = {}
      mock_db = MagicMock()
      mock_db.update_one = CoroutineMock()

      await CircuitBreaker.update(mock_id, mock_ctx, mock_db)
      mock_db.update_one.assert_called()
      bson_object_id_mock.assert_called_with(mock_id)
      expect(mock_db.update_one.await_args[0][0]['_id']).to(equal(mock_id))
  
  @pytest.mark.asyncio
  async def test_get_by_id(self, *args):
    with patch('bson.ObjectId') as object_id_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.find_one = CoroutineMock()
      object_id_mock.return_value = mock_id
      await CircuitBreaker.get_by_id(mock_id, mock_db)
      object_id_mock.assert_called_with(mock_id)
      mock_db.find_one.assert_called()
      mock_db.find_one.assert_awaited_with({'_id': mock_id})
  
  @pytest.mark.asyncio
  async def test_remove(self, *args):
    with patch('bson.ObjectId') as object_id_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.delete_one = CoroutineMock()
      await CircuitBreaker.remove(mock_id, mock_db)
      mock_db.delete_one.assert_called()
      object_id_mock.assert_called_with(mock_id)

  @pytest.mark.asyncio
  async def test_get_all(self, *args):
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await CircuitBreaker.get_all(mock_db)
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
    await CircuitBreaker.get_by_service_id(mock_service_id, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'service_id': mock_service_id})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_status_code(self, *args):
    mock_status_code = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await CircuitBreaker.get_by_status_code(mock_status_code, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'status_code': mock_status_code})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_method(self, *args):
    mock_method = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await CircuitBreaker.get_by_method(mock_method, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'method': mock_method})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_path(self, *args):
    mock_path = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await CircuitBreaker.get_by_path(mock_path, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'path': mock_path})
    mock_cursor.to_list.assert_called()
  
  @pytest.mark.asyncio
  async def test_get_by_threshold(self, *args):
    mock_thresold = 0.0
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await CircuitBreaker.get_by_threshold(mock_thresold, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'threshold': mock_thresold})
    mock_cursor.to_list.assert_called()
