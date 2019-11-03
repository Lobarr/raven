import pytest
import mock
import asynctest
from aiohttp import web
from asynctest import CoroutineMock
from expects import expect, equal, have_keys
from mock import patch, MagicMock

from api.circuit_breaker import CircuitBreaker, circuit_breaker_validator
from api.util import DB, Error, Validate, Bson
from api.circuit_breaker.controller import post_handler, get_handler, table, patch_handler, delete_handler


class TestCircuitBreakerController:
    @pytest.mark.asyncio
    async def test_post_handler(self, *args):
        with patch.object(circuit_breaker_validator, 'normalized') as normalized_mock:
            with patch.object(DB, 'get') as get_mock:
                with patch('json.loads') as loads_mock:
                    with patch.object(CircuitBreaker, 'create') as create_mock:
                        with patch.object(Error, 'handle') as handle_mock:
                            with patch.object(Validate, 'validate_schema') as validate_schema_mock:
                                mock_req = MagicMock()
                                mock_test = CoroutineMock()
                                mock_req.text = mock_test
                                loads_mock.return_value = mock_test
                                await post_handler(mock_req)
                                mock_req.text.assert_called()
                                loads_mock.assert_called()
                                validate_schema_mock.assert_called()
                                get_mock.assert_called()
                                create_mock.assert_called()
                                normalized_mock.assert_called_with(mock_test)

                                mock_err = Exception()
                                create_mock.side_effect = mock_err
                                await post_handler(mock_req)
                                handle_mock.assert_called_with(mock_err)

    @pytest.mark.asyncio
    async def test_patch_handler(self, *args):
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get') as get_mock:
                with patch('json.loads') as loads_mock:
                    with patch.object(CircuitBreaker, 'update') as update_mock:
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
                                validate_object_id_mock.assert_called_with(
                                    mock_query['id'])
                                validate_schema_mock.assert_called()
                                expect(update_mock.call_args[0][0]).to(
                                    equal(mock_query['id']))

                                mock_err = Exception()
                                update_mock.side_effect = mock_err
                                await patch_handler(mock_req)
                                handle_mock.assert_called_with(mock_err)

    @pytest.mark.asyncio
    async def test_delete_handler(self, *args):
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get') as get_mock:
                with patch.object(CircuitBreaker, 'remove') as remove_mock:
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
                        validate_object_id_mock.assert_called_with(
                            mock_ctx['id'])
                        expect(remove_mock.call_args[0][0]).to(
                            equal(mock_ctx['id']))

                        mock_err = Exception()
                        remove_mock.side_effect = mock_err
                        await delete_handler(mock_req)
                        handle_mock.assert_called_with(mock_err)

                        try:
                            mock_req.rel_url.query.get.return_value = None
                            await delete_handler(mock_req)
                        except Exception as err:
                            handle_mock.assert_called_with(err)
                            expect(err.args).to(
                                have_keys('message', 'status_code'))

    @pytest.mark.asyncio
    async def test_get_handler(self, *args):
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get') as get_mock:
                with patch.object(CircuitBreaker, 'get_all') as get_all_mock:
                    with asynctest.patch.object(CircuitBreaker, 'get_by_id') as get_by_id_mock:
                        with patch.object(CircuitBreaker, 'get_by_service_id') as get_by_service_id_mock:
                            with patch.object(CircuitBreaker, 'get_by_status_code') as get_by_status_code_mock:
                                with patch.object(CircuitBreaker, 'get_by_method') as get_by_method_mock:
                                    with patch.object(CircuitBreaker, 'get_by_threshold') as get_by_threshold_mock:
                                        with patch.object(Error, 'handle') as handle_mock:
                                            with patch.object(Bson, 'to_json') as to_json_mock:
                                                mock_req = MagicMock()
                                                mock_err = Exception()
                                                get_all_mock.side_effect = mock_err
                                                await get_handler(mock_req)
                                                handle_mock.assert_called_with(
                                                    mock_err)

                                                mock_req.rel_url.query = {}
                                                await get_handler(mock_req)
                                                get_mock.assert_called_with(
                                                    mock_req, table)
                                                get_all_mock.assert_called()

                                                mock_query = {
                                                    'id': 'some-value'
                                                }
                                                mock_req.rel_url.query = mock_query
                                                get_by_id_mock.return_value = {}
                                                await get_handler(mock_req)
                                                get_by_id_mock.assert_called()
                                                expect(
                                                    get_by_id_mock.call_args[0][0]).to(
                                                    equal(
                                                        mock_query['id']))
                                                get_mock.assert_called()

                                                mock_query = {
                                                    'service_id': 'some-value'
                                                }
                                                mock_req.rel_url.query = mock_query
                                                await get_handler(mock_req)
                                                get_by_service_id_mock.assert_called()
                                                expect(
                                                    get_by_service_id_mock.call_args[0][0]).to(
                                                    equal(
                                                        mock_query['service_id']))
                                                get_mock.assert_called()

                                                mock_query = {
                                                    'status_code': 0
                                                }
                                                mock_req.rel_url.query = mock_query
                                                await get_handler(mock_req)
                                                get_by_status_code_mock.assert_called()
                                                expect(
                                                    get_by_status_code_mock.call_args[0][0]).to(
                                                    equal(
                                                        mock_query['status_code']))
                                                get_mock.assert_called()

                                                mock_query = {
                                                    'method': 'some-value'
                                                }
                                                mock_req.rel_url.query = mock_query
                                                await get_handler(mock_req)
                                                get_by_method_mock.assert_called()
                                                expect(
                                                    get_by_method_mock.call_args[0][0]).to(
                                                    equal(
                                                        mock_query['method']))
                                                get_mock.assert_called()

                                                mock_query = {
                                                    'threshold': 0.0
                                                }
                                                mock_req.rel_url.query = mock_query
                                                await get_handler(mock_req)
                                                get_by_threshold_mock.assert_called()
                                                expect(
                                                    get_by_threshold_mock.call_args[0][0]).to(
                                                    equal(
                                                        mock_query['threshold']))
                                                get_mock.assert_called()
