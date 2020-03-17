import pytest
from mock import patch, MagicMock
from asynctest import CoroutineMock, patch as patch_async
from expects import expect, equal, raise_error, be_an, have_keys, be_true
from api.admin import AdminDTO, Admin
from api.util import Validate, Crypt, Hasher, Token


class TestAdmin:
    @pytest.mark.asyncio
    async def test_create(self, *args):
        with patch.object(Hasher, 'hash') as hash_mock:
            mock_admin = AdminDTO()
            mock_admin.password = 'some-value'
            hash_mock.return_value = mock_admin.password
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db.insert_one = CoroutineMock()
            mock_db_provider.get_mongo_collection.return_value = mock_db

            await Admin.create(mock_admin, mock_db_provider)

            mock_db_provider.get_mongo_session.assert_called()
            expect(mock_db.insert_one.call_args[0][0]).to(equal(mock_admin.to_dict()))
            hash_mock.assert_called_with(mock_admin.password)

    @pytest.mark.asyncio
    async def test_update(self, *args):
        with patch('bson.ObjectId') as bson_object_id_mock:
            with patch.object(Hasher, 'hash') as hash_mock:
                mock_id = 'some-value'
                bson_object_id_mock.return_value = mock_id
                mock_admin = AdminDTO()
                mock_admin.id = mock_id
                mock_db_provider = MagicMock()
                mock_db = MagicMock()

                mock_db.update_one = CoroutineMock()
                mock_db_provider.get_mongo_collection.return_value = mock_db

                await Admin.update(mock_admin, mock_db_provider)

                mock_db_provider.get_mongo_session.assert_called()
                mock_db.update_one.assert_called()
                bson_object_id_mock.assert_called_with(mock_id)
                expect(mock_db.update_one.await_args[0][0]['_id']).to(
                    equal(mock_id)
                )

                mock_admin = AdminDTO()
                mock_admin.id = mock_id
                mock_admin.password = 'some-value'
                hash_mock.return_value = mock_admin.password
                await Admin.update(mock_admin, mock_db_provider)
                hash_mock.assert_called_with(mock_admin.password)

    @pytest.mark.asyncio
    async def test_get_by_id(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_db_provider = MagicMock()
            mock_db = MagicMock()
            find_one_mock = CoroutineMock()

            find_one_mock.return_value = {}
            mock_db.find_one = find_one_mock
            mock_db_provider.get_mongo_collection.return_value = mock_db
            object_id_mock.return_value = mock_id

            await Admin.get_by_id(mock_id, mock_db_provider)

            object_id_mock.assert_called_with(mock_id)
            mock_db.find_one.assert_called()
            expect(mock_db.find_one.call_args[0][0]).to(equal({'_id': mock_id}))

    @pytest.mark.asyncio
    async def test_remove_by_id(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db.delete_one = CoroutineMock()
            mock_db_provider.get_mongo_collection.return_value = mock_db

            await Admin.remove_by_id(mock_id, mock_db_provider)
            
            mock_db.delete_one.assert_called()
            object_id_mock.assert_called_with(mock_id)

    @pytest.mark.asyncio
    async def test_get_all(self, *args):
        mock_db_provider = MagicMock()
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()

        mock_cursor.to_list = CoroutineMock()
        mock_cursor.to_list.return_value = []
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor
        mock_db_provider.get_mongo_collection.return_value = mock_db

        await Admin.get_all(mock_db_provider)
        
        expect(mock_db.find.call_args[0][0]).to(equal({}))
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_get_by_email(self, *args):
        mock_db_provider = MagicMock()
        mock_db = CoroutineMock()
        mock_email = 'some-value'
        mock_admin = None

        mock_db.find_one = CoroutineMock()
        mock_db.find_one.return_value = mock_admin
        mock_db_provider.get_mongo_collection.return_value = mock_db

        admin =  await Admin.get_by_email(mock_email, mock_db_provider)

        mock_db.find_one.assert_called()
        expect(mock_db.find_one.call_args[0][0]).to(equal({'email': mock_email}))
        expect(admin).to(equal(mock_admin))

    @pytest.mark.asyncio
    async def test_get_by_username(self, *args):
        mock_db_provider = MagicMock()
        mock_db = CoroutineMock()
        mock_username = 'some-value'
        mock_admin = None

        mock_db.find_one = CoroutineMock()
        mock_db.find_one.return_value = mock_admin
        mock_db_provider.get_mongo_collection.return_value = mock_db
        
        admin = await Admin.get_by_username(mock_username, mock_db_provider)

        mock_db.find_one.assert_called()
        expect(mock_db.find_one.call_args[0][0]).to(equal({'username': mock_username}))
        expect(admin).to(equal(mock_admin))

    @pytest.mark.asyncio
    async def test_verify_password(self, *args):
        with patch_async('api.admin.service.Admin.get_by_username') as get_by_username_mock:
            with patch_async('api.admin.service.Admin.generate_token') as generate_token_mock:
                with patch.object(Hasher, 'validate') as validate_mock:
                    mock_db_provider = MagicMock()
                    mock_db = MagicMock()
                    mock_db.find_one = CoroutineMock()
                    
                    mock_username = 'some-value'
                    mock_password = 'some-value'
                    mock_admin = AdminDTO()
                    mock_admin.username = mock_username
                    mock_admin.password = mock_password
                    mock_admin.id = 'some-id'

                    get_by_username_mock.return_value = mock_admin
                    validate_mock.return_value = True
                    mock_db_provider.get_mongo_collection.return_value = mock_db
                    
                    verified = await Admin.verify_password(mock_username, mock_password, mock_db_provider)
                    
                    get_by_username_mock.assert_awaited_with(
                        mock_username,
                        mock_db_provider
                    )
                    expect(validate_mock.call_args[0][0]).to(equal(mock_password))
                    expect(validate_mock.call_args[0][1]).to(
                        equal(mock_admin.password)
                    )
                    generate_token_mock.assert_called()
                    expect(verified).to(be_true)

    @pytest.mark.asyncio
    async def test_generate_token(self, *args):
        with patch_async('api.admin.service.Admin.update') as update_mock:
            with patch_async.object(Token, 'generate') as generate_mock:
                mock_db_provider = {}
                mock_token = 'some-token'

                mock_admin = AdminDTO()
                mock_admin.id = 'some-id'
                mock_admin.username = 'some-username'
                generate_mock.return_value = mock_token

                await Admin.generate_token(mock_admin, mock_db_provider)

                expect(generate_mock.call_args[0][0]).to(have_keys('_id', 'username', 'timestamp'))
                update_mock.assert_called()

    @pytest.mark.asyncio
    async def test_count(self, *args):
        mock_db_provider = MagicMock()
        mock_db = MagicMock()

        mock_db.count_documents = CoroutineMock()
        mock_db_provider.get_mongo_collection.return_value = mock_db

        await Admin.count(mock_db_provider)

        expect(mock_db.count_documents.call_args[0][0]).to(equal({}))

    @pytest.mark.asyncio
    async def test_create_default(self, *args):
        with patch_async('api.admin.service.Admin.count') as count_mock:
            with patch_async('api.admin.service.Admin.create') as create_mock:
                count_mock.return_value = 1
                mock_db_provider = MagicMock()
                mock_db = CoroutineMock()

                await Admin.create_default(mock_db)

                count_mock.assert_called_with(mock_db)
                create_mock.assert_not_awaited()

                count_mock.return_value = 0
                
                await Admin.create_default(mock_db)

                create_mock.assert_called()
