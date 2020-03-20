import pytest
# from aiohttp import web
from asynctest import CoroutineMock, patch as async_patch
from expects import expect, equal, have_keys, have_key
from mock import patch, MagicMock

# from api.admin import AdminDTO
from api.providers import DBProvider
from api.util import DB, Error, Validate, Bson
from api.admin import Admin, post_handler, patch_handler, delete_handler, get_handler, login_handler


@pytest.mark.asyncio
async def test_login_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
        with patch.object(DB, 'get_provider') as get_provider_mock:
            with patch('json.loads') as loads_mock:
                with async_patch.object(Admin, 'verify_password') as verify_password_mock:
                    with async_patch.object(Admin, 'get_by_username') as get_by_username_mock:
                        with patch.object(Error, 'handle') as handle_mock:
                            mock_request = MagicMock()
                            mock_db_provider = MagicMock()
                            mock_params = {}

                            mock_db_provider.start_mongo_transaction = CoroutineMock()
                            mock_db_provider.end_mongo_transaction = CoroutineMock()
                            mock_request.text = CoroutineMock()
                            get_provider_mock.return_value = mock_db_provider
                            deepcopy_mock.return_value = mock_db_provider
                            loads_mock.return_value = mock_params

                            await login_handler(mock_request)

                            get_provider_mock.assert_called()
                            deepcopy_mock.assert_called()
                            loads_mock.assert_called()
                            expect(handle_mock.call_args[0][0].args[0]).to(
                                have_key('message', 'Bad Request')
                            )
                            expect(handle_mock.call_args[0][0].args[0]).to(
                                have_key('status_code', 400)
                            )



                            mock_params = {
                                'username': 'some-username',
                                'password': 'some-password'
                            }
                            mock_db_provider.start_mongo_transaction = CoroutineMock()
                            mock_db_provider.end_mongo_transaction = CoroutineMock()
                            verify_password_mock.return_value = False
                            loads_mock.return_value = mock_params

                            await login_handler(mock_request)

                            get_provider_mock.assert_called()
                            deepcopy_mock.assert_called()
                            loads_mock.assert_called()
                            expect(handle_mock.call_args[0][0].args[0]).to(
                                have_key('message', 'Unauthorized')
                            )
                            expect(handle_mock.call_args[0][0].args[0]).to(
                                have_key('status_code', 401)
                            )



                            mock_db_provider.start_mongo_traansaction = CoroutineMock()
                            mock_db_provider.end_mongo_transaction = CoroutineMock()
                            verify_password_mock.return_value = True    

                            await login_handler(mock_request)

                            get_provider_mock.assert_called()
                            deepcopy_mock.assert_called()
                            loads_mock.assert_called()
                            get_by_username_mock.assert_awaited_with(mock_params['username'], mock_db_provider)
                            mock_db_provider.start_mongo_transaction.assert_awaited()
                            mock_db_provider.end_mongo_transaction.assert_awaited()



@pytest.mark.asyncio
async def test_post_handler(*args):
    with patch.object(DB, 'get_provider') as get_provider_mock:
        with patch('copy.deepcopy') as deepcopy_mock:
            with patch('json.loads') as loads_mock:
                    with async_patch.object(Admin, 'create') as create_mock:
                        with async_patch.object(Admin, 'verify_password') as verify_password_mock:
                            mock_reqeust = MagicMock()
                            mock_db_provider = MagicMock()

                            mock_db_provider.start_mongo_transaction = CoroutineMock()
                            mock_db_provider.end_mongo_transaction = CoroutineMock()
                            get_provider_mock.return_value = mock_db_provider
                            deepcopy_mock.return_value = mock_db_provider
                            mock_reqeust.text = CoroutineMock()
                            loads_mock.return_value = {}

                            response = await post_handler(mock_reqeust)

                            get_provider_mock.assert_called_with(mock_reqeust)
                            deepcopy_mock.assert_called()
                            mock_reqeust.text.assert_awaited()
                            loads_mock.assert_called()
                            create_mock.assert_awaited()
                            mock_db_provider.start_mongo_transaction.assert_awaited()
                            mock_db_provider.end_mongo_transaction.assert_awaited()

@pytest.mark.asyncio
async def test_patch_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_provider') as get_provider_mock:
                with patch('json.loads') as loads_mock:
                    with async_patch.object(Admin, 'update') as update_mock:
                        with patch.object(Error, 'handle') as handle_mock:
                                mock_request = MagicMock()
                                mock_db_provider = MagicMock()
                                mock_params = {
                                    'id': 'some-value', 
                                    'username': 'patch'
                                }
                                
                                mock_db_provider.start_mongo_transaction = CoroutineMock()
                                mock_db_provider.end_mongo_transaction = CoroutineMock()
                                get_provider_mock.return_value = mock_db_provider
                                deepcopy_mock.return_value = mock_db_provider
                                mock_request.text = CoroutineMock()
                                mock_request.rel_url.query = mock_params
                                loads_mock.return_value = mock_params

                                await patch_handler(mock_request)

                                mock_request.text.assert_called()
                                loads_mock.assert_called()
                                update_mock.assert_called()
                                mock_db_provider.start_mongo_transaction.assert_awaited()
                                mock_db_provider.end_mongo_transaction.assert_awaited()
                                get_provider_mock.assert_called_with(mock_request)
                                validate_object_id_mock.assert_called_with(
                                    mock_params['id']
                                )

                                expect(update_mock.call_args[0][0].id).to(
                                    equal(mock_params['id'])
                                )

                                mock_err = Exception()
                                update_mock.side_effect = mock_err

                                await patch_handler(mock_request)

                                handle_mock.assert_called_with(mock_err)

@pytest.mark.asyncio
async def test_delete_handler(*args):
    with patch('copy.deepcopy') as deepcopy_mock:
        with patch.object(Validate, 'validate_object_id') as validate_object_id_mock:
            with patch.object(DB, 'get_provider') as get_provider_mock:
                with async_patch.object(Admin, 'remove_by_id') as remove_by_id_mock:
                    with patch.object(Error, 'handle') as handle_mock:
                        mock_request = MagicMock()
                        mock_db_provider = MagicMock()

                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                        mock_db_provider.end_mongo_transaction = CoroutineMock()
                        get_provider_mock.return_value = mock_db_provider
                        deepcopy_mock.return_value = mock_db_provider
                        mock_request.rel_url.query.get = MagicMock()
                        mock_request.rel_url.query.get.return_value = 'some-value'
                        mock_ctx = {
                            'id': 'some-value'
                        }

                        await delete_handler(mock_request)

                        remove_by_id_mock.assert_awaited()
                        get_provider_mock.assert_called_with(mock_request)
                        validate_object_id_mock.assert_called_with(
                            mock_ctx['id']
                        )
                        expect(remove_by_id_mock.call_args[0][0]).to(
                            equal(mock_ctx['id'])
                        )

                        mock_err = Exception()
                        remove_by_id_mock.side_effect = mock_err

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
                with async_patch.object(Admin, 'get_all') as get_all_mock:
                    with async_patch.object(Admin, 'get_by_id') as get_by_id_mock:
                        with async_patch.object(Admin, 'get_by_email') as get_by_email_mock:
                            with async_patch.object(Admin, 'get_by_username') as get_by_username_mock:
                                with patch.object(Error, 'handle') as handle_mock:
                                    with patch.object(Bson, 'to_json') as to_json_mock:
                                        mock_request = MagicMock()
                                        mock_db_provider = MagicMock()
                                        mock_err = Exception()

                                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                                        mock_db_provider.end_mongo_transaction = CoroutineMock()
                                        get_provider_mock.return_value = mock_db_provider
                                        deepcopy_mock.return_value = mock_db_provider
                                        get_all_mock.side_effect = mock_err

                                        await get_handler(mock_request)

                                        handle_mock.assert_called_with(mock_err)
                                        mock_db_provider.start_mongo_transaction.assert_awaited()



                                        get_all_mock.side_effect = None
                                        mock_request.rel_url.query = {}
                                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                                        mock_db_provider.end_mongo_transaction = CoroutineMock()

                                        await get_handler(mock_request)
                                        
                                        get_provider_mock.assert_called_with(mock_request)
                                        get_all_mock.assert_called()
                                        mock_db_provider.start_mongo_transaction.assert_awaited()
                                        mock_db_provider.end_mongo_transaction.assert_awaited()




                                        mock_params = {
                                            'id': 'some-value'
                                        }

                                        mock_request.rel_url.query = mock_params
                                        get_by_id_mock.return_value = {}

                                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                                        mock_db_provider.end_mongo_transaction = CoroutineMock()

                                        await get_handler(mock_request)

                                        get_by_id_mock.assert_called()
                                        expect(get_by_id_mock.call_args[0][0]).to(
                                            equal(mock_params['id'])
                                        )
                                        get_provider_mock.assert_called()
                                        mock_db_provider.start_mongo_transaction.assert_awaited()
                                        mock_db_provider.end_mongo_transaction.assert_awaited()



                                        
                                        mock_params = {
                                            'email': 'some-value'
                                        }

                                        mock_request.rel_url.query = mock_params
                                        
                                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                                        mock_db_provider.end_mongo_transaction = CoroutineMock()

                                        await get_handler(mock_request)

                                        get_by_email_mock.assert_called()
                                        expect(get_by_email_mock.call_args[0][0]).to(
                                            equal(mock_params['email'])
                                        )
                                        get_provider_mock.assert_called()
                                        mock_db_provider.start_mongo_transaction.assert_awaited()
                                        mock_db_provider.end_mongo_transaction.assert_awaited()


                                        mock_params = {
                                            'username': 0
                                        }

                                        mock_request.rel_url.query = mock_params

                                        mock_db_provider.start_mongo_transaction = CoroutineMock()
                                        mock_db_provider.end_mongo_transaction = CoroutineMock()

                                        await get_handler(mock_request)

                                        get_by_username_mock.assert_called()
                                        expect(get_by_username_mock.call_args[0][0]).to(
                                            equal(mock_params['username'])
                                        )
                                        get_provider_mock.assert_called()
                                        mock_db_provider.start_mongo_transaction.assert_awaited()
                                        mock_db_provider.end_mongo_transaction.assert_awaited()
