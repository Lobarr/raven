import pytest
from aiohttp import web
from asynctest import CoroutineMock, patch as async_patch
from expects import expect, equal, have_keys
from mock import patch, MagicMock

from api.util import DB, Error, Validate, Bson
from api.circuit_breaker import CircuitBreaker, post_handler, get_handler, patch_handler, delete_handler


@pytest.mark.asyncio
async def test_post_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
        with patch.object(DB, 'get_provider') as get_provider_mock:
            with patch('json.loads') as loads_mock:
                with async_patch.object(CircuitBreaker, 'create') as create_mock:
                    with patch.object(Error, 'handle') as handle_mock:
                            mock_request = MagicMock()
                            mock_db_provider = MagicMock()
                            mock_circuit_breaker = {}

                            mock_db_provider.start_mongo_transaction = CoroutineMock()
                            mock_db_provider.end_mongo_transaction = CoroutineMock()
                            get_provider_mock.return_value = mock_db_provider
                            deepcopy_mock.return_value = mock_db_provider
                            mock_request.text = CoroutineMock()
                            loads_mock.return_value = mock_circuit_breaker

                            await post_handler(mock_request)

                            loads_mock.assert_called()
                            get_provider_mock.assert_called()
                            deepcopy_mock.assert_called()
                            create_mock.assert_awaited()
                            mock_db_provider.start_mongo_transaction.assert_awaited()
                            mock_db_provider.end_mongo_transaction.assert_awaited()



                            mock_err = Exception()
                            create_mock.side_effect = mock_err

                            await post_handler(mock_request)

                            handle_mock.assert_called_with(mock_err)

@pytest.mark.asyncio
async def test_patch_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
            with patch.object(DB, 'get_provider') as get_provider_mock:
                with patch('json.loads') as loads_mock:
                    with async_patch.object(CircuitBreaker, 'update') as update_mock:
                        with patch.object(CircuitBreaker, 'make_dto') as make_dto_mock:
                            with patch.object(Error, 'handle') as handle_mock:
                                mock_request = MagicMock()
                                mock_db_provider = MagicMock()
                                mock_circuit_breaker = MagicMock()
                                mock_params = {
                                    'id': 'some-value',
                                    'status': 'ON'
                                }

                                mock_db_provider.start_mongo_transaction = CoroutineMock()
                                mock_db_provider.end_mongo_transaction = CoroutineMock()
                                get_provider_mock.return_value = mock_db_provider
                                deepcopy_mock.return_value = mock_db_provider
                                mock_request.text = CoroutineMock()
                                mock_circuit_breaker.is_valid.return_value = True
                                make_dto_mock.return_value = mock_circuit_breaker

                                await patch_handler(mock_request)

                                mock_request.text.assert_called()
                                loads_mock.assert_called()
                                update_mock.assert_awaited()
                                get_provider_mock.assert_called_with(mock_request)
                                update_mock.assert_awaited_with(mock_circuit_breaker, mock_db_provider)




                                mock_validation_errors = {}
                                mock_circuit_breaker = MagicMock()
                                mock_db_provider.start_mongo_transaction = CoroutineMock()
                                mock_db_provider.end_mongo_transaction = CoroutineMock()
                                mock_circuit_breaker.is_valid.return_value = False
                                mock_circuit_breaker.get_validation_errors.return_value = mock_validation_errors
                                make_dto_mock.return_value = mock_circuit_breaker
                                
                                await patch_handler(mock_request)


                                mock_circuit_breaker.get_validation_errors.assert_called()
                                expect(handle_mock.call_args[0][0].args[0]['message']).to(
                                    equal(mock_validation_errors)
                                )


                                mock_err = Exception()
                                update_mock.side_effect = mock_err
                                mock_circuit_breaker.is_valid.return_value = True

                                await patch_handler(mock_request)

                                handle_mock.assert_called_with(mock_err)

@pytest.mark.asyncio
async def test_delete_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_provider') as get_provider_mock:
                with async_patch.object(CircuitBreaker, 'remove') as remove_mock:
                    with patch.object(Error, 'handle') as handle_mock:
                        mock_ctx = {
                            'id': 'some-value'

                        }
                        mock_request = MagicMock()
                        mock_db_provider = MagicMock()

                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                        mock_db_provider.end_mongo_transaction = CoroutineMock()
                        mock_request.rel_url.query.get = MagicMock()
                        mock_request.rel_url.query.get.return_value = mock_ctx['id']
                        deepcopy_mock.return_value = mock_db_provider
                        get_provider_mock.return_value = mock_db_provider 
                        
                        await delete_handler(mock_request)
                        
                        remove_mock.assert_awaited()
                        get_provider_mock.assert_called_with(mock_request)
                        validate_object_id_mock.assert_called_with(
                            mock_ctx['id']
                        )
                        expect(remove_mock.call_args[0][0]).to(
                            equal(mock_ctx['id'])
                        )

                        mock_err = Exception()
                        remove_mock.side_effect = mock_err

                        await delete_handler(mock_request)

                        handle_mock.assert_called_with(mock_err)

                        try:
                            mock_request.rel_url.query.get.return_value = None
                            await delete_handler(mock_request)
                        except Exception as err:
                            handle_mock.assert_called_with(err)
                            expect(err.args).to(
                                have_keys('message', 'status_code')
                            )

@pytest.mark.asyncio
async def test_get_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_provider') as get_provider_mock:
                with async_patch.object(CircuitBreaker, 'get_all') as get_all_mock:
                    with async_patch.object(CircuitBreaker, 'get_by_id') as get_by_id_mock:
                        with async_patch.object(CircuitBreaker, 'get_by_service_id') as get_by_service_id_mock:
                            with async_patch.object(CircuitBreaker, 'get_by_status_code') as get_by_status_code_mock:
                                with async_patch.object(CircuitBreaker, 'get_by_method') as get_by_method_mock:
                                    with async_patch.object(CircuitBreaker, 'get_by_threshold') as get_by_threshold_mock:
                                        with patch.object(Error, 'handle') as handle_mock:
                                            with patch.object(Bson, 'to_json') as to_json_mock:
                                                mock_request = MagicMock()
                                                mock_db_provider = MagicMock()
                                                mock_err = Exception()
                    
                                                mock_db_provider.start_mongo_transaction = CoroutineMock()
                                                mock_request.rel_url.query = {}
                                                get_all_mock.side_effect = mock_err
                                                get_provider_mock.return_value = mock_db_provider
                                                deepcopy_mock.return_value = mock_db_provider

                                                await get_handler(mock_request)

                                                mock_db_provider.start_mongo_transaction.assert_awaited()
                                                handle_mock.assert_called_with(mock_err)



                                                mock_db_provider.start_mongo_transaction = CoroutineMock()
                                                mock_db_provider.end_mongo_transaction = CoroutineMock()
                                                mock_request.rel_url.query = {}
                                                get_all_mock.side_effect = None

                                                res = await get_handler(mock_request)

                                                get_provider_mock.assert_called_with(mock_request)
                                                mock_db_provider.start_mongo_transaction.assert_awaited()
                                                mock_db_provider.end_mongo_transaction.assert_awaited()
                                                
                                                get_all_mock.assert_called()



                                                mock_params = {
                                                    'id': 'some-value'
                                                }

                                                mock_request.rel_url.query = mock_params
                                                get_by_id_mock.return_value = {}

                                                await get_handler(mock_request)

                                                get_by_id_mock.assert_called()
                                                expect(get_by_id_mock.call_args[0][0]).to(
                                                    equal(mock_params['id'])
                                                )
                                                get_provider_mock.assert_called()



                                                mock_params = {
                                                    'service_id': 'some-value'
                                                }

                                                mock_request.rel_url.query = mock_params

                                                await get_handler(mock_request)

                                                get_by_service_id_mock.assert_called()
                                                expect(get_by_service_id_mock.call_args[0][0]).to(
                                                    equal(mock_params['service_id'])
                                                )
                                                get_provider_mock.assert_called()



                                                mock_params = {
                                                    'status_code': 0
                                                }

                                                mock_request.rel_url.query = mock_params

                                                await get_handler(mock_request)

                                                get_by_status_code_mock.assert_called()
                                                expect(get_by_status_code_mock.call_args[0][0]).to(
                                                    equal(mock_params['status_code'])
                                                )
                                                get_provider_mock.assert_called()



                                                mock_params = {
                                                    'method': 'some-value'
                                                }

                                                mock_request.rel_url.query = mock_params

                                                await get_handler(mock_request)

                                                get_by_method_mock.assert_called()
                                                expect(get_by_method_mock.call_args[0][0]).to(
                                                    equal(mock_params['method'])
                                                )
                                                get_provider_mock.assert_called()



                                                mock_params = {
                                                    'threshold': 0.0
                                                }

                                                mock_request.rel_url.query = mock_params

                                                await get_handler(mock_request)

                                                get_by_threshold_mock.assert_called()
                                                expect(get_by_threshold_mock.call_args[0][0]).to(
                                                    equal(mock_params['threshold'])
                                                )
                                                get_provider_mock.assert_called()
