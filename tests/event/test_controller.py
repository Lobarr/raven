import pytest
import mock
import asynctest
from aiohttp import web
from asynctest import CoroutineMock
from expects import expect, equal, have_keys
from mock import patch, MagicMock

from api.event import Event, event_validator
from api.util import DB, Error, Validate, Bson
from api.event.controller import post_handler, get_handler, table, patch_handler, delete_handler

class TestEventController:
  @pytest.mark.asyncio
  async def test_post_handler(self, *args):
    with patch.object(DB, 'get') as get_mock:
      with patch('json.loads') as loads_mock:
        with patch.object(Event, 'create') as create_mock:
          with patch.object(Error, 'handle') as handle_mock:
            with patch.object(Validate, 'validate_schema') as validate_schema_mock:
              mock_req = MagicMock()
              mock_req.text = CoroutineMock()
              await post_handler(mock_req)
              mock_req.text.assert_called()
              loads_mock.assert_called()
              validate_schema_mock.assert_called()
              get_mock.assert_called()
              create_mock.assert_called()
              
              mock_err = Exception()
              create_mock.side_effect = mock_err
              await post_handler(mock_req)
              handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_patch_handler(self, *args):
    with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
      with patch.object(DB, 'get') as get_mock:
        with patch('json.loads') as loads_mock:
          with patch.object(Event, 'update') as update_mock:
            with patch.object(Error, 'handle') as handle_mock:
              with patch.object(Validate, 'validate_schema') as validate_schema_mock:
                mock_req = MagicMock()
                mock_req.text = CoroutineMock()
                mock_query = {
                  'id': 'some-value'
                }
                mock_req.rel_url.query = mock_query
                await patch_handler(mock_req)
                mock_req.text.assert_called()
                loads_mock.assert_called()
                update_mock.assert_called()
                get_mock.assert_called_with(mock_req, table)
                validate_object_id_mock.assert_called_with(mock_query['id'])
                validate_schema_mock.assert_called()
                expect(update_mock.call_args[0][0]).to(equal(mock_query['id']))
                
                mock_err = Exception()
                update_mock.side_effect = mock_err
                await patch_handler(mock_req)
                handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_delete_handler(self, *args):
    with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
      with patch.object(DB, 'get') as get_mock:
        with patch.object(Event, 'remove') as remove_mock:
          with patch.object(Error, 'handle') as handle_mock:
            mock_req = MagicMock()
            mock_req.rel_url.query.get = MagicMock()
            mock_req.rel_url.query.get.return_value = 'some-value'
            mock_ctx = {
              'id': 'some-value'
            }
            await delete_handler(mock_req)
            remove_mock.assert_called()
            get_mock.assert_called_with(mock_req, table)
            validate_object_id_mock.assert_called_with(mock_ctx['id'])
            expect(remove_mock.call_args[0][0]).to(equal(mock_ctx['id']))
            
            mock_err = Exception()
            remove_mock.side_effect = mock_err
            await delete_handler(mock_req)
            handle_mock.assert_called_with(mock_err)

            try:
              mock_req.rel_url.query.get.return_value = None
              await delete_handler(mock_req)
            except Exception as err:
              handle_mock.assert_called_with(err)
              expect(err.args).to(have_keys('message', 'status_code'))
  
  @pytest.mark.asyncio
  async def test_get_handler(self, *args):
    with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
      with patch.object(DB, 'get') as get_mock:
        with patch.object(Event, 'get_all') as get_all_mock:
          with asynctest.patch.object(Event, 'get_by_id') as get_by_id_mock:
            with patch.object(Event, 'get_by_circuit_breaker_id') as get_by_circuit_breaker_id_mock:
              with patch.object(Event, 'get_by_target') as get_by_target_mock:
                with patch.object(Error, 'handle') as handle_mock:
                  with patch.object(Bson, 'to_json') as to_json_mock:
                    mock_req = MagicMock()
                    mock_err = Exception()
                    get_all_mock.side_effect = mock_err
                    await get_handler(mock_req)
                    handle_mock.assert_called_with(mock_err)

                    mock_req.rel_url.query = {}
                    await get_handler(mock_req)
                    get_mock.assert_called_with(mock_req, table)
                    get_all_mock.assert_called()
                    
                    mock_query = {
                      'id': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    get_by_id_mock.return_value = {}
                    await get_handler(mock_req)
                    get_by_id_mock.assert_called()
                    expect(get_by_id_mock.call_args[0][0]).to(equal(mock_query['id']))
                    get_mock.assert_called()

                    mock_query = {
                      'circuit_breaker_id': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    await get_handler(mock_req)
                    get_by_circuit_breaker_id_mock.assert_called()
                    expect(get_by_circuit_breaker_id_mock.call_args[0][0]).to(equal(mock_query['circuit_breaker_id']))
                    get_mock.assert_called()

                    mock_query = {
                      'target': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    await get_handler(mock_req)
                    get_by_target_mock.assert_called()
                    expect(get_by_target_mock.call_args[0][0]).to(equal(mock_query['target']))
                    get_mock.assert_called()
