import pytest
import mock
from aiohttp import web
from asynctest import CoroutineMock
from expects import expect, equal, have_keys
from mock import patch, MagicMock

from api.service import Service, service_validator
from api.util import DB, Error, Validate, Bson
from api.service.controller import post_handler, get_handler, table, put_handler, delete_handler

class TestSericeController:
  @pytest.mark.asyncio
  async def test_post_handler(self, *args):
    with patch.object(DB, 'get') as get_mock:
      with patch('json.loads') as loads_mock:
        with patch.object(Service, 'create') as create_mock:
          with patch.object(Error, 'handle') as handle_mock:
            with patch.object(service_validator, 'validate') as validate_mock:
              mock_req = MagicMock()
              mock_req.text = CoroutineMock()
              await post_handler(mock_req)
              mock_req.text.assert_called()
              loads_mock.assert_called()
              validate_mock.assert_called()
              get_mock.assert_called_with(mock_req, table)
              create_mock.assert_called()
              
              mock_err = Exception()
              create_mock.side_effect = mock_err
              await post_handler(mock_req)
              handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_put_handler(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get') as get_mock:
        with patch('json.loads') as loads_mock:
          with patch.object(Service, 'update') as update_mock:
            with patch.object(Error, 'handle') as handle_mock:
              with patch.object(service_validator, 'validate') as validate_mock:
                mock_req = MagicMock()
                mock_req.text = CoroutineMock()
                mock_ctx = {
                  'id': 'some-value'
                }
                loads_mock.return_value = mock_ctx
                await put_handler(mock_req)
                mock_req.text.assert_called()
                loads_mock.assert_called()
                update_mock.assert_called()
                get_mock.assert_called_with(mock_req, table)
                object_id_mock.assert_called_with(mock_ctx['id'])
                validate_mock.assert_called()
                expect(update_mock.call_args[0][0]).to(equal(mock_ctx['id']))
                
                mock_err = Exception()
                update_mock.side_effect = mock_err
                await put_handler(mock_req)
                handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_delete_handler(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get') as get_mock:
        with patch.object(Service, 'remove') as remove_mock:
          with patch.object(Error, 'handle') as handle_mock:
            mock_req = MagicMock()
            mock_req._rel_url.query.get = MagicMock()
            mock_req._rel_url.query.get.return_value = 'some-value'
            mock_ctx = {
              'id': 'some-value'
            }
            await delete_handler(mock_req)
            remove_mock.assert_called()
            get_mock.assert_called_with(mock_req, table)
            object_id_mock.assert_called_with(mock_ctx['id'])
            expect(remove_mock.call_args[0][0]).to(equal(mock_ctx['id']))
            
            mock_err = Exception()
            remove_mock.side_effect = mock_err
            await delete_handler(mock_req)
            handle_mock.assert_called_with(mock_err)

            try:
              mock_req._rel_url.query.get.return_value = None
              await delete_handler(mock_req)
            except Exception as err:
              handle_mock.assert_called_with(err)
              expect(err.args).to(have_keys('message', 'status_code'))
  
  @pytest.mark.asyncio
  async def test_get_handler(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get') as get_mock:
        with patch.object(Service, 'get_all') as get_all_mock:
          with patch.object(Service, 'get_by_id') as get_by_id_mock:
            with patch.object(Service, 'get_by_state') as get_by_state_mock:
              with patch.object(Service, 'get_by_secure') as get_by_secure_mock:
                with patch.object(Error, 'handle') as handle_mock:
                  with patch.object(Bson, 'to_json') as to_json_mock:
                    mock_req = MagicMock()
                    mock_req._rel_url.query = {}
                    await get_handler(mock_req)
                    get_mock.assert_called_with(mock_req, table)
                    get_all_mock.assert_called()

                    mock_query = {
                      'id': 'some-value'
                    }
                    mock_req._rel_url.query = mock_query
                    await get_handler(mock_req)
                    get_by_id_mock.assert_called()
                    expect(get_by_id_mock.call_args[0][0]).to(equal(mock_query['id']))
                    get_mock.assert_called()

                    mock_query = {
                      'state': 'some-value'
                    }
                    mock_req._rel_url.query = mock_query
                    await get_handler(mock_req)
                    get_by_state_mock.assert_called()
                    expect(get_by_state_mock.call_args[0][0]).to(equal(mock_query['state']))
                    get_mock.assert_called()

                    mock_query = {
                      'secure': 'true'
                    }
                    mock_req._rel_url.query = mock_query
                    await get_handler(mock_req)
                    get_by_secure_mock.assert_called()
                    expect(get_by_secure_mock.call_args[0][0]).to(equal(bool(mock_query['secure'])))
                    get_mock.assert_called()


