import pytest
import mock
import asynctest
from aiohttp import web
from asynctest import CoroutineMock
from expects import expect, equal, have_keys
from mock import patch, MagicMock

from api.rate_limiter import RateLimiter, rate_limit_rule_validator, rate_limit_entry_validator
from api.util import DB, Error, Validate, Bson
from api.rate_limiter.controller import create_rule, update_rule, delete_rule, retrieve_rule, create_entry, update_entry, delete_entry, retrieve_entry

class TestRateLimiterController:
  @pytest.mark.asyncio
  async def test_create_rule(self, *args):
    with patch.object(DB, 'get_redis') as get_redis_mock:
      with patch('json.loads') as loads_mock:
        with patch.object(RateLimiter, 'create_rule') as create_rule_mock:
          with patch.object(Error, 'handle') as handle_mock:
            with patch.object(Validate, 'schema') as validate_mock:
              mock_req = MagicMock()
              mock_test = CoroutineMock()
              mock_req.text = mock_test
              loads_mock.return_value = mock_test
              await create_rule(mock_req)
              mock_req.text.assert_called()
              loads_mock.assert_called()
              validate_mock.assert_called()
              get_redis_mock.assert_called()
              get_redis_mock.assert_called()
              create_rule_mock.assert_called()
              
              mock_err = Exception()
              create_rule_mock.side_effect = mock_err
              await create_rule(mock_req)
              handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_update_rule(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get_redis') as get_redis_mock:
        with patch('json.loads') as loads_mock:
          with patch.object(RateLimiter, 'update_rule') as update_mock:
            with patch.object(Error, 'handle') as handle_mock:
              with patch.object(Validate, 'schema') as validate_mock:
                mock_req = MagicMock()
                mock_req.text = CoroutineMock()
                mock_query = {
                  'id': 'some-value'
                }
                mock_req.rel_url.query = mock_query
                await update_rule(mock_req)
                mock_req.text.assert_called()
                loads_mock.assert_called()
                update_mock.assert_called()
                get_redis_mock.assert_called_with(mock_req)
                object_id_mock.assert_called_with(mock_query['id'])
                validate_mock.assert_called()
                expect(update_mock.call_args[0][0]).to(equal(mock_query['id']))
                
                mock_err = Exception()
                update_mock.side_effect = mock_err
                await update_rule(mock_req)
                handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_delete_rule(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get_redis') as get_redis_mock:
        with patch.object(RateLimiter, 'delete_rule') as remove_mock:
          with patch.object(Error, 'handle') as handle_mock:
            mock_req = MagicMock()
            mock_req.rel_url.query.get = MagicMock()
            mock_req.rel_url.query.get.return_value = 'some-value'
            mock_ctx = {
              'id': 'some-value'
            }
            await delete_rule(mock_req)
            remove_mock.assert_called()
            get_redis_mock.assert_called_with(mock_req)
            object_id_mock.assert_called_with(mock_ctx['id'])
            expect(remove_mock.call_args[0][0]).to(equal(mock_ctx['id']))
            
            mock_err = Exception()
            remove_mock.side_effect = mock_err
            await delete_rule(mock_req)
            handle_mock.assert_called_with(mock_err)

            try:
              mock_req.rel_url.query.get.return_value = None
              await delete_rule(mock_req)
            except Exception as err:
              handle_mock.assert_called_with(err)
              expect(err.args).to(have_keys('message', 'status_code'))
  
  @pytest.mark.asyncio
  async def test_retrieve_rule(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get_redis') as get_mock:
        with patch.object(RateLimiter, 'get_all_rules') as get_all_rules_mock:
          with asynctest.patch.object(RateLimiter, 'get_rule_by_id') as get_rule_by_id_mock:
            with patch.object(RateLimiter, 'get_rule_by_status_code') as get_rule_by_status_code_mock:
              with patch.object(RateLimiter, 'get_rule_by_service_id') as get_rule_by_service_id_mock:
                with patch.object(Error, 'handle') as handle_mock:
                  with patch.object(Bson, 'to_json') as to_json_mock:
                    mock_req = MagicMock()
                    mock_err = Exception()
                    get_all_rules_mock.side_effect = mock_err
                    await retrieve_rule(mock_req)
                    handle_mock.assert_called_with(mock_err)

                    mock_req.rel_url.query = {}
                    await retrieve_rule(mock_req)
                    get_mock.assert_called_with(mock_req)
                    get_all_rules_mock.assert_called()
                    
                    mock_query = {
                      'id': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    get_rule_by_id_mock.return_value = {}
                    await retrieve_rule(mock_req)
                    get_rule_by_id_mock.assert_called()
                    expect(get_rule_by_id_mock.call_args[0][0]).to(equal(mock_query['id']))
                    get_mock.assert_called()

                    mock_query = {
                      'status_code': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    await retrieve_rule(mock_req)
                    get_rule_by_status_code_mock.assert_called()
                    expect(get_rule_by_status_code_mock.call_args[0][0]).to(equal(mock_query['status_code']))
                    get_mock.assert_called()

                    mock_query = {
                      'service_id': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    await retrieve_rule(mock_req)
                    get_rule_by_service_id_mock.assert_called()
                    expect(get_rule_by_service_id_mock.call_args[0][0]).to(equal(mock_query['service_id']))
                    get_mock.assert_called()


  @pytest.mark.asyncio
  async def test_create_entry(self, *args):
    with patch.object(DB, 'get_redis') as get_redis_mock:
      with patch('json.loads') as loads_mock:
        with patch.object(RateLimiter, 'create_entry') as create_entry_rule:
          with patch.object(Error, 'handle') as handle_mock:
            with patch.object(Validate, 'schema') as validate_mock:
              mock_req = MagicMock()
              mock_test = CoroutineMock()
              mock_req.text = mock_test
              loads_mock.return_value = mock_test
              await create_entry(mock_req)
              mock_req.text.assert_called()
              loads_mock.assert_called()
              validate_mock.assert_called()
              get_redis_mock.assert_called()
              get_redis_mock.assert_called()
              create_entry_rule.assert_called()
              
              mock_err = Exception()
              create_entry_rule.side_effect = mock_err
              await create_entry(mock_req)
              handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_update_entry(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get_redis') as get_redis_mock:
        with patch('json.loads') as loads_mock:
          with patch.object(RateLimiter, 'update_entry') as update_mock:
            with patch.object(Error, 'handle') as handle_mock:
              with patch.object(Validate, 'schema') as validate_mock:
                mock_req = MagicMock()
                mock_req.text = CoroutineMock()
                mock_query = {
                  'id': 'some-value'
                }
                mock_req.rel_url.query = mock_query
                await update_entry(mock_req)
                mock_req.text.assert_called()
                loads_mock.assert_called()
                update_mock.assert_called()
                get_redis_mock.assert_called_with(mock_req)
                object_id_mock.assert_called_with(mock_query['id'])
                validate_mock.assert_called()
                expect(update_mock.call_args[0][0]).to(equal(mock_query['id']))
                
                mock_err = Exception()
                update_mock.side_effect = mock_err
                await update_entry(mock_req)
                handle_mock.assert_called_with(mock_err)

  @pytest.mark.asyncio
  async def test_delete_entry(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get_redis') as get_redis_mock:
        with patch.object(RateLimiter, 'delete_entry') as remove_mock:
          with patch.object(Error, 'handle') as handle_mock:
            mock_req = MagicMock()
            mock_req.rel_url.query.get = MagicMock()
            mock_req.rel_url.query.get.return_value = 'some-value'
            mock_ctx = {
              'id': 'some-value'
            }
            await delete_entry(mock_req)
            remove_mock.assert_called()
            get_redis_mock.assert_called_with(mock_req)
            object_id_mock.assert_called_with(mock_ctx['id'])
            expect(remove_mock.call_args[0][0]).to(equal(mock_ctx['id']))
            
            mock_err = Exception()
            remove_mock.side_effect = mock_err
            await delete_entry(mock_req)
            handle_mock.assert_called_with(mock_err)

            try:
              mock_req.rel_url.query.get.return_value = None
              await delete_entry(mock_req)
            except Exception as err:
              handle_mock.assert_called_with(err)
              expect(err.args).to(have_keys('message', 'status_code'))
  
  @pytest.mark.asyncio
  async def test_retrieve_entry(self, *args):
    with patch.object(Validate, 'object_id') as object_id_mock:
      with patch.object(DB, 'get_redis') as get_mock:
        with asynctest.patch.object(RateLimiter, 'get_all_entries') as get_all_entries_mock:
          with asynctest.asynctest.patch.object(RateLimiter, 'get_entry_by_id') as get_entry_by_id_mock:
            with asynctest.patch.object(RateLimiter, 'get_entry_by_rule_id') as get_entry_by_rule_id_mock:
              with asynctest.patch.object(RateLimiter, 'get_entry_by_host') as get_entry_by_host_mock:
                with patch.object(Error, 'handle') as handle_mock:
                  with patch.object(Bson, 'to_json') as to_json_mock:
                    mock_req = MagicMock()
                    mock_err = Exception()
                    get_all_entries_mock.side_effect = mock_err
                    await retrieve_entry(mock_req)
                    handle_mock.assert_called_with(mock_err)

                    mock_req.rel_url.query = {}
                    await retrieve_entry(mock_req)
                    get_mock.assert_called_with(mock_req)
                    get_all_entries_mock.assert_called()
                    
                    mock_query = {
                      'id': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    get_entry_by_id_mock.return_value = {}
                    await retrieve_entry(mock_req)
                    get_entry_by_id_mock.assert_called()
                    expect(get_entry_by_id_mock.call_args[0][0]).to(equal(mock_query['id']))
                    get_mock.assert_called()

                    mock_query = {
                      'rule_id': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    await retrieve_entry(mock_req)
                    get_entry_by_rule_id_mock.assert_called()
                    expect(get_entry_by_rule_id_mock.call_args[0][0]).to(equal(mock_query['rule_id']))
                    get_mock.assert_called()

                    mock_query = {
                      'host': 'some-value'
                    }
                    mock_req.rel_url.query = mock_query
                    await retrieve_entry(mock_req)
                    get_entry_by_host_mock.assert_called()
                    expect(get_entry_by_host_mock.call_args[0][0]).to(equal(mock_query['host']))
                    get_mock.assert_called()
