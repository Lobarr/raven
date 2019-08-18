import pytest 
import asyncio
import mock
import asynctest
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys, have_key, contain
from api.circuit_breaker import CircuitBreaker, circuit_breaker_validator
from api.util import Validate, Crypt
from api.service import Service

class TestCircuitBreaker:
  @pytest.mark.asyncio
  async def test_create(self, *args):
    with asynctest.patch.object(Service, 'check_exists') as check_exists_mock:
      mock_ctx = {}
      mock_db = MagicMock()
      mock_db.insert_one = CoroutineMock()
      await CircuitBreaker.create(mock_ctx, mock_db, mock_db)
      mock_db.insert_one.assert_awaited_with(mock_ctx)

      mock_ctx = {
        'service_id': 'some-value'
      }
      await CircuitBreaker.create(mock_ctx, mock_db, mock_db)
      check_exists_mock.assert_called()

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

  @pytest.mark.asyncio
  async def test_check_exists(self, *args):
    with asynctest.patch.object(CircuitBreaker, 'get_by_id') as get_mock:
      try:
        mock_id = 'some-value'
        mock_db = MagicMock()
        get_mock.return_value = None
        await CircuitBreaker.check_exists(mock_id, mock_db)
        get_mock.assert_called()
      except Exception as err:
        expect(err.args[0]).to(have_keys('message', 'status_code'))

  @pytest.mark.asyncio
  async def test_incr_tripped_count(self, *args):
    with patch('bson.ObjectId') as bson_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.update_one = CoroutineMock()
      bson_mock.return_value = mock_id
      await CircuitBreaker.incr_tripped_count(mock_id, mock_db)
      mock_db.update_one.assert_awaited()
      bson_mock.assert_called_with(mock_id)
      expect(mock_db.update_one.call_args[0][0]['_id']).to(equal(mock_id))
      expect(mock_db.update_one.call_args[0][1]['$inc']).to(have_key('tripped_count', 1))

  def test_count_key(self, *args):
    mock_id = 'some-value'
    res = CircuitBreaker.count_key(mock_id)
    expect(res).to(contain(mock_id))
    expect(res).to(contain('count'))

  def test_queued_key(self, *args):
    mock_id = 'some-value'
    res = CircuitBreaker.queued_key(mock_id)
    expect(res).to(contain(mock_id))
    expect(res).to(contain('queued'))

  @pytest.mark.asyncio
  async def test_incr_count(self, *args):
    with patch.object(CircuitBreaker, 'count_key') as count_key_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.incr = CoroutineMock()
      expected_count_key = 'some-value'
      count_key_mock.return_value = expected_count_key
      await CircuitBreaker.incr_count(mock_id, mock_db)
      mock_db.incr.assert_awaited_with(expected_count_key)

  @pytest.mark.asyncio
  async def test_get_count(self, *args):
    with patch.object(CircuitBreaker, 'count_key') as count_key_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      expected_count_key = 'some-value'
      mock_db.get = CoroutineMock()
      count_key_mock.return_value = expected_count_key
      await CircuitBreaker.get_count(mock_id, mock_db)
      count_key_mock.assert_called_with(mock_id)
      mock_db.get.assert_awaited_with(expected_count_key, encoding='utf-8')

  @pytest.mark.asyncio
  async def test_set_count(self, *args):
    with patch.object(CircuitBreaker, 'count_key') as count_key_mock:
      mock_id = 'some-value'
      mock_count = 1
      mock_timeout = 5
      expected_count_key = 'some-value'
      mock_db = MagicMock()
      mock_db.set = CoroutineMock()
      count_key_mock.return_value = expected_count_key
      await CircuitBreaker.set_count(mock_id, mock_count, mock_timeout, mock_db)
      count_key_mock.assert_called_with(mock_id)
      mock_db.set.assert_awaited_with(expected_count_key, mock_count, expire=mock_timeout)

  @pytest.mark.asyncio
  async def test_get_queued(self, *args):
    with patch.object(CircuitBreaker, 'queued_key') as queued_key_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      expected_count_key = 'some-value'
      mock_db.get = CoroutineMock()
      queued_key_mock.return_value = expected_count_key
      await CircuitBreaker.get_queued(mock_id, mock_db)
      queued_key_mock.assert_called_with(mock_id)
      mock_db.get.assert_awaited_with(expected_count_key, encoding='utf-8')

  @pytest.mark.asyncio
  async def test_set_queued(self, *args):
    with patch.object(CircuitBreaker, 'queued_key') as queued_key_mock:
      mock_id = 'some-id'
      mock_queued = 'some-queued'
      mock_timeout = 5
      expected_count_key = 'some-cout_key'
      mock_db = MagicMock()
      mock_db.set = CoroutineMock()
      queued_key_mock.return_value = expected_count_key
      await CircuitBreaker.set_queued(mock_id, mock_queued, mock_timeout, mock_db)
      queued_key_mock.assert_called_with(mock_id)
      mock_db.set.assert_awaited_with(expected_count_key, mock_queued, expire=mock_timeout)
