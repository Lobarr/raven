import pytest
import pydash
import mock
import asynctest
from aiohttp import web
from asynctest import CoroutineMock
from expects import expect, equal, have_keys, raise_error
from mock import patch, MagicMock
from api.endpoint_cacher import EndpointCacher, endpoint_cache_validator
from api.util import DB, Error, Validate, Bson
from api.endpoint_cacher.controller import post_handler, get_handler, patch_handler, delete_handler, patch_handler_response_codes


class TestEndpointCacherController:
    @pytest.mark.asyncio
    async def test_post_handler(self, *args):
        with patch.object(DB, 'get') as get_mock:
            with patch.object(DB, 'get_redis') as get_redis_mock:
                with patch('json.loads') as loads_mock:
                    with patch.object(EndpointCacher, 'create') as create_mock:
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
                                get_redis_mock.assert_called()
                                create_mock.assert_called()

                                mock_err = Exception()
                                create_mock.side_effect = mock_err
                                await post_handler(mock_req)
                                handle_mock.assert_called_with(mock_err)

    @pytest.mark.asyncio
    async def test_patch_handler(self, *args):
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_redis') as get_redis_mock:
                with patch('json.loads') as loads_mock:
                    with patch.object(EndpointCacher, 'update') as update_mock:
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
                                get_redis_mock.assert_called_with(mock_req)
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
    async def test_patch_handler_response_codes(self, *args):
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_redis') as get_redis_mock:
                with patch('json.loads') as loads_mock:
                    with asynctest.patch.object(EndpointCacher, 'add_status_codes') as add_status_codes_mock:
                        with asynctest.patch.object(EndpointCacher, 'remove_status_codes') as remove_status_codes_mock:
                            with patch.object(Error, 'handle') as handle_mock:
                                with patch.object(Validate, 'validate_schema') as validate_schema_mock:
                                    get_redis_mock.return_value = {}
                                    mock_query = {
                                        'id': 'some-value',
                                        'action': 'add'
                                    }
                                    mock_ctx = {
                                        'response_codes': [200]
                                    }
                                    mock_req = MagicMock()
                                    mock_req.text = CoroutineMock()
                                    mock_req.rel_url.query = mock_query
                                    loads_mock.return_value = mock_ctx
                                    await patch_handler_response_codes(mock_req)
                                    validate_object_id_mock.assert_called_with(
                                        mock_query['id'])
                                    validate_schema_mock.assert_called_with(
                                        mock_ctx, endpoint_cache_validator)
                                    add_status_codes_mock.assert_called_with(
                                        mock_ctx['response_codes'], mock_query['id'], {})

                                    mock_query = pydash.merge(
                                        mock_query, {'action': 'remove'})
                                    mock_req.rel_url.query = mock_query
                                    await patch_handler_response_codes(mock_req)
                                    remove_status_codes_mock.assert_called_with(
                                        mock_ctx['response_codes'], mock_query['id'], {})

                                    try:
                                        mock_err = Exception
                                        remove_status_codes_mock.side_effect = mock_err
                                        await patch_handler_response_codes(mock_req)
                                    except Exception as err:
                                        handle_mock.assert_called_with(err)

    @pytest.mark.asyncio
    async def test_delete_handler(self, *args):
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_redis') as get_redis_mock:
                with patch.object(EndpointCacher, 'delete') as remove_mock:
                    with patch.object(Error, 'handle') as handle_mock:
                        mock_req = MagicMock()
                        mock_req.rel_url.query.get = MagicMock()
                        mock_req.rel_url.query.get.return_value = 'some-value'
                        mock_ctx = {
                            'id': 'some-value'
                        }
                        await delete_handler(mock_req)
                        remove_mock.assert_called()
                        get_redis_mock.assert_called_with(mock_req)
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
            with patch.object(DB, 'get_redis') as get_mock:
                with patch.object(EndpointCacher, 'get_all') as get_all_mock:
                    with asynctest.patch.object(EndpointCacher, 'get_by_id') as get_by_id_mock:
                        with patch.object(EndpointCacher, 'get_by_service_id') as get_by_service_id_mock:
                            with patch.object(Error, 'handle') as handle_mock:
                                with patch.object(Bson, 'to_json') as to_json_mock:
                                    mock_req = MagicMock()
                                    mock_err = Exception()
                                    get_all_mock.side_effect = mock_err
                                    await get_handler(mock_req)
                                    handle_mock.assert_called_with(mock_err)

                                    mock_req.rel_url.query = {}
                                    await get_handler(mock_req)
                                    get_mock.assert_called_with(mock_req)
                                    get_all_mock.assert_called()

                                    mock_query = {
                                        'id': 'some-value'
                                    }
                                    mock_req.rel_url.query = mock_query
                                    get_by_id_mock.return_value = {}
                                    await get_handler(mock_req)
                                    get_by_id_mock.assert_called()
                                    expect(get_by_id_mock.call_args[0][0]).to(
                                        equal(mock_query['id']))
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
