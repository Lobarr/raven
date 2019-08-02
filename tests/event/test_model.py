import pytest 
import asyncio
import mock
import asynctest
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys
from api.event import Event, event_validator
from api.util import Validate, Crypt

class TestEvent:
  @pytest.mark.asyncio
  async def test_create(self, *args):
    mock_ctx = {}
    mock_db = MagicMock()
    mock_db.insert_one = CoroutineMock()
    await Event.create(mock_ctx, mock_db)
    mock_db.insert_one.assert_awaited_with(mock_ctx)

  @pytest.mark.asyncio
  async def test_update(self, *args):
    with patch('bson.ObjectId') as bson_object_id_mock:
      mock_id = 'some-value'
      bson_object_id_mock.return_value = mock_id  
      mock_ctx = {}
      mock_db = MagicMock()
      mock_db.update_one = CoroutineMock()

      await Event.update(mock_id, mock_ctx, mock_db)
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
      await Event.get_by_id(mock_id, mock_db)
      object_id_mock.assert_called_with(mock_id)
      mock_db.find_one.assert_called()
      mock_db.find_one.assert_awaited_with({'_id': mock_id})
  
  @pytest.mark.asyncio
  async def test_remove(self, *args):
    with patch('bson.ObjectId') as object_id_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_db.delete_one = CoroutineMock()
      await Event.remove(mock_id, mock_db)
      mock_db.delete_one.assert_called()
      object_id_mock.assert_called_with(mock_id)

  @pytest.mark.asyncio
  async def test_get_all(self, *args):
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await Event.get_all(mock_db)
    mock_db.find.assert_called_with({})
    mock_cursor.to_list.assert_called()
  
  @pytest.mark.asyncio
  async def test_get_by_circuit_breaker_id(self, *args):
    mock_circuit_breaker_mock = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await Event.get_by_circuit_breaker_id(mock_circuit_breaker_mock, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'circuit_breaker_id': mock_circuit_breaker_mock})
    mock_cursor.to_list.assert_called()

  @pytest.mark.asyncio
  async def test_get_by_target(self, *args):
    mock_target = 'some-value'
    mock_db = CoroutineMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = CoroutineMock()
    mock_db.find = MagicMock()
    mock_db.find.return_value = mock_cursor
    await Event.get_by_target(mock_target, mock_db)
    mock_db.find.assert_called()
    mock_db.find.assert_called_with({'target': mock_target})
    mock_cursor.to_list.assert_called()
  
  @pytest.mark.asyncio
  async def test_handle_event(self, *args):
    with patch('requests.post') as post_req_mock:
      mock_ctx = {
        'target': 'some-value',
        'body': {},
        'headers': {}
      }
      await Event.handle_event(mock_ctx)
      post_req_mock.assert_called_with(url=mock_ctx['target'], data=mock_ctx['body'], headers=mock_ctx['headers'])
