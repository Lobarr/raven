import pytest
import asyncio
import mock
import asynctest
from motor.motor_asyncio import AsyncIOMotorCursor
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys, be_above, be_below
from api.service import Service, service_validator
from api.util import Validate, Crypt


class TestService:
    @pytest.mark.asyncio
    async def test_create(self, *args):
        mock_ctx = {}
        mock_db = MagicMock()
        mock_db.insert_one = CoroutineMock()
        await Service.create(mock_ctx, mock_db)
        mock_db.insert_one.assert_awaited_with(mock_ctx)

    @pytest.mark.asyncio
    async def test_update(self, *args):
        with patch('bson.ObjectId') as bson_object_id_mock:
            mock_id = 'some-value'
            bson_object_id_mock.return_value = mock_id
            mock_ctx = {}
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()

            await Service.update(mock_id, mock_ctx, mock_db)
            mock_db.update_one.assert_called()
            bson_object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.await_args[0][0]['_id']).to(
                equal(mock_id))

    @pytest.mark.asyncio
    async def test_get_by_id(self, *args):
        with patch('bson.ObjectId') as bson_object_id_mock:
            mock_id = 'some-value'
            bson_object_id_mock.return_value = mock_id
            mock_db = MagicMock()
            mock_db.find_one = CoroutineMock()

            await Service.get_by_id(mock_id, mock_db)
            mock_db.find_one.assert_called()
            bson_object_id_mock.assert_called_with(mock_id)
            expect(mock_db.find_one.await_args[0][0]['_id']).to(equal(mock_id))

    @pytest.mark.asyncio
    async def test_get_by_state(self, *args):
        mock_state = 'some-value'
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list = CoroutineMock()
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor
        await Service.get_by_state(mock_state, mock_db)
        mock_db.find.assert_called()
        mock_db.find.assert_called_with({'state': mock_state})
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_get_by_secure(self, *args):
        mock_secure = True
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list = CoroutineMock()
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor
        await Service.get_by_secure(mock_secure, mock_db)
        mock_db.find.assert_called()
        mock_db.find.assert_called_with({'secure': mock_secure})
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_get_by_path(self, *args):
        mock_path = 'some-value'
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list = CoroutineMock()
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor
        await Service.get_by_path(mock_path, mock_db)
        mock_db.find.assert_called()
        mock_db.find.assert_called_with({'path': mock_path})
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_get_all(self, *args):
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list = CoroutineMock()
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor
        await Service.get_all(mock_db)
        mock_db.find.assert_called_with({})
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_remove(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_db = MagicMock()
            mock_db.delete_one = CoroutineMock()
            await Service.remove(mock_id, mock_db)
            mock_db.delete_one.assert_called()
            object_id_mock.assert_called_with(mock_id)

    @pytest.mark.asyncio
    async def test_add_target(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_target = 'some-value'
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()
            await Service.add_target(mock_id, mock_target, mock_db)
            mock_db.update_one.assert_called()
            object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.call_args[0][1]['$push']['targets']).to(
                equal(mock_target))

    @pytest.mark.asyncio
    async def test_remove_target(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_target = 'some-value'
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()
            await Service.remove_target(mock_id, mock_target, mock_db)
            mock_db.update_one.assert_called()
            object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.call_args[0][1]['$pull']['targets']).to(
                equal(mock_target))

    @pytest.mark.asyncio
    async def test_advance_target(self, *args):
        with asynctest.patch.object(Service, 'get_by_id') as get_by_id_mock:
            with asynctest.patch.object(Service, 'update') as update_mock:
                mock_id = 'some-value'
                mock_db = MagicMock()
                mock_service = {
                    'targets': [],
                }
                get_by_id_mock.return_value = mock_service
                await Service.advance_target(mock_id, mock_db)
                update_mock.assert_not_awaited()

                mock_service = {
                    'targets': [
                        'some-value',
                        'some-value'
                    ],
                    'cur_target_index': 0
                }
                get_by_id_mock.return_value = mock_service
                await Service.advance_target(mock_id, mock_db)
                update_mock.assert_called()
                expect(update_mock.call_args[0][0]).to(equal(mock_id))
                expect(update_mock.call_args[0][1]['cur_target_index']).to(
                    be_above(mock_service['cur_target_index']))
                expect(update_mock.call_args[0][2]).to(equal(mock_db))

                mock_service = {
                    'targets': [
                        'some-value',
                        'some-value'
                    ],
                    'cur_target_index': 1
                }
                get_by_id_mock.return_value = mock_service
                await Service.advance_target(mock_id, mock_db)
                update_mock.assert_called()
                expect(update_mock.call_args[0][0]).to(equal(mock_id))
                expect(update_mock.call_args[0][1]['cur_target_index']).to(
                    be_below(mock_service['cur_target_index']))
                expect(update_mock.call_args[0][2]).to(equal(mock_db))

    @pytest.mark.asyncio
    async def test_add_whitelist(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_host = 'some-value'
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()
            await Service.add_whitelist(mock_id, mock_host, mock_db)
            mock_db.update_one.assert_called()
            object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.call_args[0][1]['$push']['whitelisted_hosts']).to(
                equal(mock_host))

    @pytest.mark.asyncio
    async def test_remove_whitelist(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_host = 'some-value'
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()
            await Service.remove_whitelist(mock_id, mock_host, mock_db)
            mock_db.update_one.assert_called()
            object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.call_args[0][1]['$pull']['whitelisted_hosts']).to(
                equal(mock_host))

    @pytest.mark.asyncio
    async def test_add_blacklist(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_host = 'some-value'
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()
            await Service.add_blacklist(mock_id, mock_host, mock_db)
            mock_db.update_one.assert_called()
            object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.call_args[0][1]['$push']['blacklisted_hosts']).to(
                equal(mock_host))

    @pytest.mark.asyncio
    async def test_remove_blacklist(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_host = 'some-value'
            mock_db = MagicMock()
            mock_db.update_one = CoroutineMock()
            await Service.remove_blacklist(mock_id, mock_host, mock_db)
            mock_db.update_one.assert_called()
            object_id_mock.assert_called_with(mock_id)
            expect(
                mock_db.update_one.call_args[0][1]['$pull']['blacklisted_hosts']).to(
                equal(mock_host))

    @pytest.mark.asyncio
    async def test_check_exists(self, *args):
        with asynctest.patch.object(Service, 'get_by_id') as get_mock:
            try:
                mock_id = 'some-value'
                mock_db = MagicMock()
                get_mock.return_value = None
                await Service.check_exists(mock_id, mock_db)
            except Exception as err:
                get_mock.assert_called()
                expect(err.args[0]).to(have_keys('message', 'status_code'))
