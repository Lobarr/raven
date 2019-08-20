import asynctest
import pytest
import pydash
from api.endpoint_cacher import EndpointCacher
from api.endpoint_cacher.model import endpoint_cache_service_id_index, endpoint_cache_endpoint_index
from api.util import DB
from api.service import Service
from mock import MagicMock, patch
from asynctest import CoroutineMock
from expects import expect, equal, be_a, be_true, contain, have_keys, have_len, raise_error

class TestEndpointCacher:
  @pytest.mark.asyncio
  async def test__set_indexes(self, *args):
    mock_ctx = {
      '_id': 'some-value',
      'service_id': 'some-id',
      'endpoint': 'some-endpoint'
    }
    mock_db = MagicMock()
    mock_hset = CoroutineMock()
    mock_db.hset = mock_hset
    await EndpointCacher._set_indexes(mock_ctx, mock_db)
    expect(mock_hset.await_count).to(equal(2))
    for call in mock_hset.await_args_list:
      expect([endpoint_cache_endpoint_index, endpoint_cache_service_id_index]).to(contain(call[0][0]))
      expect(call[0][1]).to(equal(mock_ctx['_id']))
      expect([mock_ctx['service_id'], mock_ctx['endpoint']]).to(contain(call[0][2]))

  @pytest.mark.asyncio
  async def test__clear_indexes(self, *args):
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hdel = CoroutineMock()
    mock_db.hdel = mock_hdel
    await EndpointCacher._clear_indexes(mock_id, mock_db)
    expect(mock_hdel.await_count).to(equal(2))
    for call in mock_hdel.await_args_list:
      expect([endpoint_cache_endpoint_index, endpoint_cache_service_id_index]).to(contain(call[0][0]))
      expect(call[0][1]).to(equal(mock_id))

  @pytest.mark.asyncio
  async def test__search_indexes(self, *args):
    expected_id = 'some-id'
    mock_index = 'some-index'
    mock_search = 'some-search'
    mock_db = MagicMock()
    mock_hscan = CoroutineMock()
    mock_hscan.return_value = (None, [(expected_id.encode('utf-8'), mock_search.encode('utf-8'))])
    mock_db.hscan = mock_hscan
    keys = await EndpointCacher._search_indexes(mock_index, mock_search, mock_db)
    mock_hscan.assert_awaited()
    expect(keys).to(contain(expected_id))

  @pytest.mark.asyncio
  async def test_create(self, *args):
    with asynctest.patch.object(Service, 'check_exists') as check_exists_mock:
      with asynctest.patch.object(EndpointCacher, '_set_indexes') as _set_indexes_mock:
        mock_ctx = {
          'service_id': 'some-id',
          'response_codes': [200],
          'timeout': 2
        }
        mock_endpoint_cacher_db = MagicMock()
        mock_service_db = MagicMock()
        mock_sadd = CoroutineMock()
        mock_hmset_dict = CoroutineMock()
        mock_endpoint_cacher_db.sadd = mock_sadd
        mock_endpoint_cacher_db.hmset_dict = mock_hmset_dict
        await EndpointCacher.create(mock_ctx, mock_endpoint_cacher_db, mock_service_db)
        check_exists_mock.assert_awaited()
        _set_indexes_mock.assert_called()
        expect(mock_hmset_dict.await_args[0][1]).to(have_keys('service_id', 'response_codes', '_id'))
        expect(mock_hmset_dict.await_args[0][1]['service_id']).to(equal(mock_ctx['service_id']))
        expect(mock_sadd.await_count).to(equal(2))

  @pytest.mark.asyncio
  async def test_update(self, *args):
    with patch('pydash.merge') as merge_mock:
      with asynctest.patch.object(EndpointCacher, '_set_indexes') as _set_indexes_mock:
        mock_id = 'some-value'
        mock_ctx = {}
        mock_db = MagicMock()
        mock_hmset_dict = CoroutineMock()
        mock_db.hmset_dict = mock_hmset_dict
        await EndpointCacher.update(mock_id, mock_ctx, mock_db)
        expect(merge_mock.call_args[0][0]).to(equal(mock_ctx))
        expect(merge_mock.call_args[0][1]['_id']).to(equal(mock_id))
        _set_indexes_mock.assert_awaited()
        mock_hmset_dict.assert_awaited_with(mock_id, mock_ctx)

  @pytest.mark.asyncio
  async def test_delete(self, *args):
    with asynctest.patch.object(EndpointCacher, '_clear_indexes') as _clear_indexes_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_delete = CoroutineMock()
      mock_sadd = CoroutineMock()
      mock_db.delete = mock_delete
      mock_db.srem  = mock_sadd
      await EndpointCacher.delete(mock_id, mock_db)
      mock_delete.assert_awaited_with(mock_id)
      _clear_indexes_mock.assert_awaited_with(mock_id, mock_db)
      mock_sadd.assert_awaited()
      expect(mock_sadd.await_args[0][1]).to(equal(mock_id))

  @pytest.mark.asyncio
  async def test_get_by_id(self, *args):
    response_codes_id = 'some-id'
    expected_cache = {
      'endpoint': 'some-endpoint',
      'timeout': 10,
      'response_codes': response_codes_id,
      '_id': 'some-id'
    }
    expected_response_codes = [200, 300]
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hgetall = CoroutineMock()
    mock_smembers = CoroutineMock()
    mock_hgetall.return_value = expected_cache
    mock_smembers.return_value = expected_response_codes
    mock_db.hgetall = mock_hgetall
    mock_db.smembers = mock_smembers
    cache = await EndpointCacher.get_by_id(mock_id, mock_db)
    mock_hgetall.assert_awaited()
    expect(mock_hgetall.await_args[0][0]).to(equal(mock_id))
    mock_smembers.assert_awaited()
    expect(mock_smembers.await_args[0][0]).to(equal(response_codes_id))
    expect(cache).to(equal(pydash.merge(expected_cache, {'response_codes': expected_response_codes})))

  @pytest.mark.asyncio
  async def test_get_by_service_id(self, *args):
    with asynctest.patch.object(EndpointCacher, '_search_indexes') as _search_indes_mock:
      response_codes_id = 'some-id'
      expected_cache = {
        'endpoint': 'some-endpoint',
        'timeout': 10,
        'response_codes': response_codes_id,
        '_id': 'some-id'
      }
      expected_response_codes = [200, 300]
      mock_service_id = 'some-value'
      mock_keys = ['some-id']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_smembers = CoroutineMock()
      _search_indes_mock.return_value = mock_keys
      mock_hgetall.return_value = expected_cache
      mock_db.hgetall = mock_hgetall
      mock_db.smembers = mock_smembers
      mock_smembers.return_value = expected_response_codes
      caches = await EndpointCacher.get_by_service_id(mock_service_id, mock_db)
      _search_indes_mock.assert_awaited_with(endpoint_cache_service_id_index, mock_service_id, mock_db)
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_keys[0]))
      mock_smembers.assert_awaited()
      expect(mock_smembers.await_args[0][0]).to(equal(response_codes_id))
      expect(caches).to(have_len(1))
      expect(caches[0]).to(equal(pydash.merge(expected_cache, {'response_codes': expected_response_codes})))

  
  @pytest.mark.asyncio
  async def test_get_by_endpoint(self, *args):
    with asynctest.patch.object(EndpointCacher, '_search_indexes') as _search_indes_mock:
      response_codes_id = 'some-id'
      expected_cache = {
        'endpoint': 'some-endpoint',
        'timeout': 10,
        'response_codes': response_codes_id,
        '_id': 'some-id'
      }
      expected_response_codes = [200, 300]
      mock_endpoint = 'some-value'
      mock_keys = ['some-id']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_smembers = CoroutineMock()
      _search_indes_mock.return_value = mock_keys
      mock_hgetall.return_value = expected_cache
      mock_db.hgetall = mock_hgetall
      mock_db.smembers = mock_smembers
      mock_smembers.return_value = expected_response_codes
      caches = await EndpointCacher.get_by_endpoint(mock_endpoint, mock_db)
      _search_indes_mock.assert_awaited_with(endpoint_cache_endpoint_index, mock_endpoint, mock_db)
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_keys[0]))
      mock_smembers.assert_awaited()
      expect(mock_smembers.await_args[0][0]).to(equal(response_codes_id))
      expect(caches).to(have_len(1))
      expect(caches[0]).to(equal(pydash.merge(expected_cache, {'response_codes': expected_response_codes})))
  
  @pytest.mark.asyncio
  async def test_get_all(self, *args):
    with asynctest.patch.object(DB, 'fetch_members') as fetch_members_mock:
      response_codes_id = 'some-id'
      expected_cache = {
        'endpoint': 'some-endpoint',
        'timeout': 10,
        'response_codes': response_codes_id,
        '_id': 'some-id'
      }
      expected_response_codes = [200, 300]
      mock_keys = ['some-id']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_smembers = CoroutineMock()
      fetch_members_mock.return_value = mock_keys
      mock_hgetall.return_value = expected_cache
      mock_db.hgetall = mock_hgetall
      mock_db.smembers = mock_smembers
      mock_smembers.return_value = expected_response_codes
      caches = await EndpointCacher.get_all(mock_db)
      fetch_members_mock.assert_awaited()
      mock_hgetall.assert_awaited()
      mock_smembers.assert_awaited()
      expect(mock_smembers.await_args[0][0]).to(equal(response_codes_id))
      expect(caches).to(have_len(1))
      expect(caches[0]).to(equal(pydash.merge(expected_cache, {'response_codes': expected_response_codes})))

  @pytest.mark.asyncio
  async def test_add_status_code(self, *args):
    mock_cache = {
      'endpoint': 'some-endpoint',
      'timeout': 10,
      '_id': 'some-id'
    }
    mock_status_codes = [200]
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hgetall = CoroutineMock()
    mock_sadd = CoroutineMock()
    mock_hgetall.return_value = mock_cache
    mock_db.hgetall = mock_hgetall
    mock_db.sadd = mock_sadd

    try:
      await EndpointCacher.add_status_codes(mock_status_codes, mock_id, mock_db)
    except Exception as err:
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_id))  
    
    mock_cache = pydash.merge(mock_cache, {'response_codes': 'some-value'})
    await EndpointCacher.add_status_codes(mock_status_codes, mock_id, mock_db)
    expect(mock_sadd.await_count).to(equal(len(mock_status_codes)))


  @pytest.mark.asyncio
  async def test_remove_status_code(self, *args):
    mock_cache = {
      'endpoint': 'some-endpoint',
      'timeout': 10,
      '_id': 'some-id'
    }
    mock_status_codes = [200]
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hgetall = CoroutineMock()
    mock_srem = CoroutineMock()
    mock_hgetall.return_value = mock_cache
    mock_db.hgetall = mock_hgetall
    mock_db.srem = mock_srem

    try:
      await EndpointCacher.remove_status_codes(mock_status_codes, mock_id, mock_db)
    except Exception as err:
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_id))  
    
    mock_cache = pydash.merge(mock_cache, {'response_codes': 'some-value'})
    await EndpointCacher.remove_status_codes(mock_status_codes, mock_id, mock_db)
    expect(mock_srem.await_count).to(equal(len(mock_status_codes)))
