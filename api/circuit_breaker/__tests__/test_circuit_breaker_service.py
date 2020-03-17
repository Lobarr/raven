import pytest
import asyncio
import mock

from mock import patch, MagicMock
from asynctest import CoroutineMock, patch as async_patch
from expects import expect, equal, raise_error, be_an, have_keys, have_key, contain
from api.circuit_breaker import CircuitBreaker, CircuitBreakerDTO
from api.util import Validate, Crypt
from api.service import Service


class TestCircuitBreaker:
    @pytest.mark.asyncio
    async def test_create(self, *args):
        with async_patch.object(Service, 'check_exists') as check_exists_mock:
            circuit_breaker = CircuitBreakerDTO()
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db.insert_one = CoroutineMock()
            mock_db_provider.get_mongo_collection.return_value = mock_db

            await CircuitBreaker.create(circuit_breaker, mock_db_provider)

            mock_db.insert_one.assert_awaited()
            mock_db_provider.get_mongo_session.assert_called()

            circuit_breaker = CircuitBreaker.make_dto({
                'service_id': 'some-id'
            })

            await CircuitBreaker.create(circuit_breaker, mock_db_provider)

            check_exists_mock.assert_called()

    @pytest.mark.asyncio
    async def test_update(self, *args):
        with patch('bson.ObjectId') as bson_object_id_mock:
            mock_id = 'some-value'
            bson_object_id_mock.return_value = mock_id
            circuit_breaker = CircuitBreaker.make_dto({
                'id': mock_id
            })
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db.update_one = CoroutineMock()
            mock_db_provider.get_mongo_collection.return_value = mock_db

            await CircuitBreaker.update(circuit_breaker, mock_db_provider)

            mock_db_provider.get_mongo_collection.assert_called()
            mock_db.update_one.assert_called()
            bson_object_id_mock.assert_called_with(mock_id)
            expect(mock_db.update_one.await_args[0][0]['_id']).to(
                equal(mock_id)
            )

    @pytest.mark.asyncio
    async def test_get_by_id(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_db_provider = MagicMock()
            mock_db = MagicMock()
            
            mock_db_provider.get_mongo_collection.return_value = mock_db
            mock_db.find_one = CoroutineMock()
            object_id_mock.return_value = mock_id

            await CircuitBreaker.get_by_id(mock_id, mock_db_provider)

            mock_db_provider.get_mongo_session.assert_called()
            object_id_mock.assert_called_with(mock_id)
            mock_db.find_one.assert_called()
            expect(mock_db.find_one.call_args[0][0]).to(equal({'_id': mock_id}))

    @pytest.mark.asyncio
    async def test_remove(self, *args):
        with patch('bson.ObjectId') as object_id_mock:
            mock_id = 'some-value'
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db_provider.get_mongo_collection.return_value = mock_db
            mock_db.delete_one = CoroutineMock()

            await CircuitBreaker.remove(mock_id, mock_db_provider)
            
            mock_db_provider.get_mongo_session.assert_called()
            mock_db.delete_one.assert_called()
            object_id_mock.assert_called_with(mock_id)

    @pytest.mark.asyncio
    async def test_get_all(self, *args):
        mock_db_provider = MagicMock()
        mock_db = MagicMock()
        mock_cursor = MagicMock()

        mock_db_provider.get_mongo_collection.return_value = mock_db
        mock_cursor.to_list = CoroutineMock()
        mock_cursor.to_list.return_value = []
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor

        await CircuitBreaker.get_all(mock_db_provider)
        
        mock_db_provider.get_mongo_session.assert_called()
        mock_db.find.assert_called()
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_get_by_service_id(self, *args):
        mock_service_id = 'some-value'
        mock_db_provider = MagicMock()
        mock_db = CoroutineMock()

        mock_db_provider.get_mongo_collection.return_value = mock_db
        mock_db.find_one = CoroutineMock()
        mock_db.find_one.return_value = {}

        await CircuitBreaker.get_by_service_id(mock_service_id, mock_db_provider)

        mock_db_provider.get_mongo_session.assert_called()
        mock_db.find_one.assert_awaited()
        expect(mock_db.find_one.call_args[0][0]).to(equal({'service_id': mock_service_id}))

    @pytest.mark.asyncio
    async def test_get_by_status_code(self, *args):
        mock_status_code = 200
        mock_db_provider = MagicMock()
        mock_db = MagicMock()
        mock_cursor = MagicMock()

        mock_db_provider.get_mongo_collection.return_value = mock_db
        mock_cursor.to_list = CoroutineMock()
        mock_cursor.to_list.return_value = []
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor

        await CircuitBreaker.get_by_status_code(mock_status_code, mock_db_provider)

        mock_db_provider.get_mongo_session.assert_called()
        mock_db.find.assert_called()
        expect(mock_db.find.call_args[0][0]).to(equal({'status_code': mock_status_code}))
        mock_cursor.to_list.assert_called()

    @pytest.mark.asyncio
    async def test_get_by_method(self, *args):
        mock_method = 'some-value'
        mock_db_provider = MagicMock()
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()

        mock_db_provider.get_mongo_collection.return_value = mock_db
        mock_cursor.to_list = CoroutineMock()
        mock_cursor.to_list.return_value = []
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor

        await CircuitBreaker.get_by_method(mock_method, mock_db_provider)


        mock_db_provider.get_mongo_session.assert_called()
        mock_db.find.assert_called()
        expect(mock_db.find.call_args[0][0]).to(equal({'method': mock_method}))

    @pytest.mark.asyncio
    async def test_get_by_threshold(self, *args):
        mock_thresold = 0.0
        mock_db_provider = MagicMock()
        mock_db = CoroutineMock()
        mock_cursor = MagicMock()

        mock_db_provider.get_mongo_collection.return_value = mock_db
        mock_cursor.to_list = CoroutineMock()
        mock_db.find = MagicMock()
        mock_db.find.return_value = mock_cursor

        await CircuitBreaker.get_by_threshold(mock_thresold, mock_db_provider)
        
        mock_db.find.assert_called()
        expect(mock_db.find.call_args[0][0]).to(equal({'threshold': mock_thresold}))

    @pytest.mark.asyncio
    async def test_check_exists(self, *args):
        with async_patch.object(CircuitBreaker, 'get_by_id') as get_mock:
            try:
                mock_id = 'some-value'
                mock_db = MagicMock()

                get_mock.return_value = None

                await CircuitBreaker.check_exists(mock_id, mock_db)

                get_mock.assert_called()
            except Exception as err:
                expect(err.args[0]).to(have_keys('message', 'status_code'))

    @pytest.mark.asyncio
    async def test_incr_tripped_count(self, *args):
        with patch('bson.ObjectId') as bson_mock:
            mock_id = 'some-value'
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db_provider.get_mongo_collection.return_value = mock_db
            # mock_db_provider.get_mongo_session = CoroutineMock()
            mock_db.update_one = CoroutineMock()
            bson_mock.return_value = mock_id

            await CircuitBreaker.incr_tripped_count(mock_id, mock_db_provider)

            mock_db_provider.get_mongo_session.assert_called()
            mock_db.update_one.assert_awaited()
            bson_mock.assert_called_with(mock_id)
            expect(mock_db.update_one.call_args[0][0]['_id']).to(
                equal(mock_id)
            )
            expect(mock_db.update_one.call_args[0][1]['$inc']).to(
                have_key('tripped_count', 1)
            )

    def test_count_key(self, *args):
        mock_id = 'some-value'

        res = CircuitBreaker.count_key(mock_id)

        expect(res).to(contain(mock_id))
        expect(res).to(contain('count'))

    def test_queued_key(self, *args):
        mock_id = 'some-value'

        res = CircuitBreaker.queued_key(mock_id)

        expect(res).to(contain(mock_id))
        expect(res).to(contain('queued'))

    @pytest.mark.asyncio
    async def test_incr_count(self, *args):
        with patch.object(CircuitBreaker, 'count_key') as count_key_mock:
            mock_id = 'some-value'
            mock_db = MagicMock()
            mock_db.incr = CoroutineMock()
            expected_count_key = 'some-value'
            count_key_mock.return_value = expected_count_key
            await CircuitBreaker.incr_count(mock_id, mock_db)
            mock_db.incr.assert_awaited_with(expected_count_key)

    @pytest.mark.asyncio
    async def test_get_count(self, *args):
        with patch.object(CircuitBreaker, 'count_key') as count_key_mock:
            mock_id = 'some-value'
            expected_count_key = 'some-value'
            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db_provider.get_redis.return_value = mock_db
            mock_db.get = CoroutineMock()
            count_key_mock.return_value = expected_count_key

            await CircuitBreaker.get_count(mock_id, mock_db_provider)

            count_key_mock.assert_called_with(mock_id)
            mock_db.get.assert_awaited_with(
                expected_count_key, encoding='utf-8')

    @pytest.mark.asyncio
    async def test_set_count(self, *args):
        with patch.object(CircuitBreaker, 'count_key') as count_key_mock:
            mock_id = 'some-value'
            mock_count = 1
            mock_timeout = 5
            expected_count_key = 'some-value'
            
            mock_db_provider = MagicMock()
            mock_db = MagicMock()
            
            mock_db_provider.get_redis.return_value = mock_db
            mock_db.set = CoroutineMock()
            count_key_mock.return_value = expected_count_key

            await CircuitBreaker.set_count(mock_id, mock_count, mock_timeout, mock_db_provider)

            count_key_mock.assert_called_with(mock_id)
            mock_db.set.assert_awaited_with(
                expected_count_key, mock_count, 
                expire=mock_timeout
            )

    @pytest.mark.asyncio
    async def test_get_queued(self, *args):
        with patch.object(CircuitBreaker, 'queued_key') as queued_key_mock:
            mock_id = 'some-value'
            expected_count_key = 'some-value'

            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db_provider.get_redis.return_value = mock_db
            mock_db.get = CoroutineMock()
            queued_key_mock.return_value = expected_count_key

            await CircuitBreaker.get_queued(mock_id, mock_db_provider)

            queued_key_mock.assert_called_with(mock_id)
            mock_db.get.assert_awaited_with(
                expected_count_key, encoding='utf-8')

    @pytest.mark.asyncio
    async def test_set_queued(self, *args):
        with patch.object(CircuitBreaker, 'queued_key') as queued_key_mock:
            mock_id = 'some-id'
            mock_queued = 'some-queued'
            mock_timeout = 5
            expected_count_key = 'some-cout_key'

            mock_db_provider = MagicMock()
            mock_db = MagicMock()

            mock_db_provider.get_redis.return_value = mock_db
            mock_db.set = CoroutineMock()
            queued_key_mock.return_value = expected_count_key

            await CircuitBreaker.set_queued(mock_id, mock_queued, mock_timeout, mock_db_provider)

            queued_key_mock.assert_called_with(mock_id)
            mock_db.set.assert_awaited_with(
                expected_count_key, mock_queued, expire=mock_timeout)
