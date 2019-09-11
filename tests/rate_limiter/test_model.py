import asynctest
import pytest
from mock import MagicMock, patch
from expects import expect, contain, equal, have_keys, have_key
from asynctest import CoroutineMock
from api.rate_limiter import RateLimiter
from api.rate_limiter.model import entry_rule_id_index, entry_host_index, rule_status_code_index
from api.util import DB, Async

class TestRateLimiter:
  @pytest.mark.asyncio
  @asynctest.patch.object(Async, 'all')
  async def test_set_indexes(self, *args):
    mock_ctx = {
      '_id': 'some-value',
      'path': 'some-path', 
      'host': 'some-host',
      'status_code': 'some-value',
      'rule_id': 'some-value', 
    }
    mock_db = MagicMock()
    mock_hset = CoroutineMock()
    mock_db.hset = mock_hset
    await RateLimiter._set_indexes(mock_ctx, mock_db)
    args[0].assert_awaited()
    for call in mock_hset.await_args_list:
      expect([rule_status_code_index, entry_rule_id_index, entry_host_index]).to(contain(call[0][0]))
      expect(call[0][1]).to(equal(mock_ctx['_id']))
      expect([mock_ctx[key] for key in mock_ctx.keys()]).to(contain(call[0][2]))
  
  @pytest.mark.asyncio
  @asynctest.patch.object(Async, 'all')
  async def test__clear_indexes(self, *args):
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hdel = CoroutineMock()
    mock_db.hdel = mock_hdel
    await RateLimiter._clear_indexes(mock_id, mock_db)
    args[0].assert_awaited()
    for call in mock_hdel.await_args_list:
      expect([rule_status_code_index, entry_rule_id_index, entry_host_index]).to(contain(call[0][0]))
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
    keys = await RateLimiter._search_indexes(mock_index, mock_search, mock_db)
    mock_hscan.assert_awaited()
    expect(keys).to(contain(expected_id))

  

  @pytest.mark.asyncio
  async def test_create_rule(self, *args):
    with asynctest.patch.object(RateLimiter, '_set_indexes') as _set_indexes_mock:
      mock_ctx = {
        'path': 'some-path',
        'max_requests': 1,
        'timeout': 1,
        'host': 'some-host',
        'message': 'some-message'
      }
      mock_db = MagicMock()
      mock_service_db = MagicMock()
      mock_sadd = CoroutineMock()
      mock_hmset_dict = CoroutineMock()
      mock_db.sadd = mock_sadd
      mock_db.hmset_dict = mock_hmset_dict
      await RateLimiter.create_rule(mock_ctx, mock_db)
      _set_indexes_mock.assert_called()
      mock_sadd.assert_awaited()
      for key in mock_ctx.keys():
        expect(mock_hmset_dict.await_args[0][1]).to(have_key(key))
        expect(mock_hmset_dict.await_args[0][1][key]).to(equal(mock_ctx[key]))
    
  @pytest.mark.asyncio
  async def test_update_rule(self, *args):
    with patch('pydash.merge') as merge_mock:
      with asynctest.patch.object(RateLimiter, '_set_indexes') as _set_indexes_mock:
        mock_id = 'some-value'
        mock_ctx = {}
        mock_db = MagicMock()
        mock_hmset_dict = CoroutineMock()
        mock_db.hmset_dict = mock_hmset_dict
        await RateLimiter.update_rule(mock_id, mock_ctx, mock_db)
        expect(merge_mock.call_args[0][0]).to(equal(mock_ctx))
        expect(merge_mock.call_args[0][1]['_id']).to(equal(mock_id))
        _set_indexes_mock.assert_awaited()
        mock_hmset_dict.assert_awaited_with(mock_id, mock_ctx)

  @pytest.mark.asyncio
  async def test_delete_rule(self, *args):
    with asynctest.patch.object(RateLimiter, '_clear_indexes') as _clear_indexes_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_delete = CoroutineMock()
      mock_sadd = CoroutineMock()
      mock_db.delete = mock_delete
      mock_db.srem  = mock_sadd
      await RateLimiter.delete_rule(mock_id, mock_db)
      mock_delete.assert_awaited_with(mock_id)
      _clear_indexes_mock.assert_awaited_with(mock_id, mock_db)
      mock_sadd.assert_awaited()
      expect(mock_sadd.await_args[0][1]).to(equal(mock_id))

  
  @pytest.mark.asyncio
  async def test_get_rule_by_id(self, *args):
    expected_rule = {
      'path': 'some-path',
      'max_requests': 1,
      'timeout': 1,
      'host': 'some-host',
      'message': 'some-message'
    }
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hgetall = CoroutineMock()
    mock_hgetall.return_value = expected_rule
    mock_db.hgetall = mock_hgetall
    cache = await RateLimiter.get_rule_by_id(mock_id, mock_db)
    mock_hgetall.assert_awaited()
    expect(mock_hgetall.await_args[0][0]).to(equal(mock_id))
    expect(cache).to(equal(expected_rule))

  @pytest.mark.asyncio
  @asynctest.patch.object(Async, 'all')
  async def test_get_rule_by_status_code(self, *args):
    with asynctest.patch.object(RateLimiter, '_search_indexes') as _search_indexes_mock:
      mock_rule = {
        'path': 'some-path',
        'max_requests': 1,
        'timeout': 1,
        'host': 'some-host',
        'message': 'some-message'
      }
      mock_status_code = 1
      mock_keys = ['some-value']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_db.hgetall = mock_hgetall
      _search_indexes_mock.return_value = mock_keys
      mock_hgetall.return_value = mock_rule
      args[0].return_value = [mock_rule]
      rules = await RateLimiter.get_rule_by_status_code(mock_status_code, mock_db)
      args[0].assert_awaited()
      _search_indexes_mock.assert_awaited()
      expect(mock_hgetall.call_args[0][0]).to(equal(mock_keys[0]))
      expect(rules).to(contain(mock_rule))

  @pytest.mark.asyncio
  async def test_get_all_rules(self, *args):
    with asynctest.patch.object(DB, 'fetch_members') as fetch_members_mock:
      mock_rule = {
        'path': 'some-path',
        'max_requests': 1,
        'timeout': 1,
        'host': 'some-host',
        'message': 'some-message'
      }
      mock_keys = ['some-value']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_db.hgetall = mock_hgetall
      fetch_members_mock.return_value = mock_keys
      mock_hgetall.return_value = mock_rule
      rules = await RateLimiter.get_all_rules(mock_db)
      fetch_members_mock.assert_awaited()
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_keys[0]))
      expect(rules).to(contain(mock_rule))

  @pytest.mark.asyncio
  async def test_create_entry(self, *args):
    with asynctest.patch.object(RateLimiter, '_set_indexes') as _set_indexes_mock:
      mock_ctx = {
        'rule_id': 'some-id',
        'host': 'some-host',
        'timeout': 1,
      }
      mock_db = MagicMock()
      mock_service_db = MagicMock()
      mock_sadd = CoroutineMock()
      mock_hmset_dict = CoroutineMock()
      mock_expire = CoroutineMock()
      mock_db.sadd = mock_sadd
      mock_db.hmset_dict = mock_hmset_dict
      mock_db.expire = mock_expire
      await RateLimiter.create_entry(mock_ctx, mock_db)
      _set_indexes_mock.assert_called()
      mock_sadd.assert_awaited()
      for key in mock_ctx.keys():
        expect(mock_hmset_dict.await_args[0][1]).to(have_key(key))
        expect(mock_hmset_dict.await_args[0][1][key]).to(equal(mock_ctx[key]))
    
  @pytest.mark.asyncio
  async def test_update_entry(self, *args):
    with patch('pydash.merge') as merge_mock:
      with asynctest.patch.object(RateLimiter, '_set_indexes') as _set_indexes_mock:
        mock_id = 'some-value'
        mock_ctx = {}
        mock_db = MagicMock()
        mock_hmset_dict = CoroutineMock()
        mock_db.hmset_dict = mock_hmset_dict
        await RateLimiter.update_entry(mock_id, mock_ctx, mock_db)
        expect(merge_mock.call_args[0][0]).to(equal(mock_ctx))
        expect(merge_mock.call_args[0][1]['_id']).to(equal(mock_id))
        _set_indexes_mock.assert_awaited()
        mock_hmset_dict.assert_awaited_with(mock_id, mock_ctx)

  @pytest.mark.asyncio
  async def test_delete_entry(self, *args):
    with asynctest.patch.object(RateLimiter, '_clear_indexes') as _clear_indexes_mock:
      mock_id = 'some-value'
      mock_db = MagicMock()
      mock_delete = CoroutineMock()
      mock_sadd = CoroutineMock()
      mock_db.delete = mock_delete
      mock_db.srem  = mock_sadd
      await RateLimiter.delete_entry(mock_id, mock_db)
      mock_delete.assert_awaited_with(mock_id)
      _clear_indexes_mock.assert_awaited_with(mock_id, mock_db)
      mock_sadd.assert_awaited()
      expect(mock_sadd.await_args[0][1]).to(equal(mock_id))

  @pytest.mark.asyncio
  async def test_get_entry_by_id(self, *args):
    expected_entry = {
      'rule_id': 'some-id',
      'host': 'some-host',
      'timeout': 1,
    }
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hgetall = CoroutineMock()
    mock_hgetall.return_value = expected_entry
    mock_db.hgetall = mock_hgetall
    cache = await RateLimiter.get_entry_by_id(mock_id, mock_db)
    mock_hgetall.assert_awaited()
    expect(mock_hgetall.await_args[0][0]).to(equal(mock_id))
    expect(cache).to(equal(expected_entry))

  @pytest.mark.asyncio
  async def test_get_entry_by_rule_id(self, *args):
    with asynctest.patch.object(RateLimiter, '_search_indexes') as _search_indexes_mock:
      mock_rule = {
        'rule_id': 'some-id',
        'host': 'some-host',
        'timeout': 1,
      }
      mock_rule_id = 'some-value'
      mock_keys = ['some-value']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_db.hgetall = mock_hgetall
      _search_indexes_mock.return_value = mock_keys
      mock_hgetall.return_value = mock_rule
      rules = await RateLimiter.get_entry_by_rule_id(mock_rule_id, mock_db)
      _search_indexes_mock.assert_awaited()
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_keys[0]))
      expect(rules).to(contain(mock_rule))


  @pytest.mark.asyncio
  async def test_get_entry_by_host(self, *args):
    with asynctest.patch.object(RateLimiter, '_search_indexes') as _search_indexes_mock:
      mock_rule = {
        'rule_id': 'some-id',
        'host': 'some-host',
        'timeout': 1,
      }
      mock_host = 'some-value'
      mock_keys = ['some-value']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_db.hgetall = mock_hgetall
      _search_indexes_mock.return_value = mock_keys
      mock_hgetall.return_value = mock_rule
      rules = await RateLimiter.get_entry_by_host(mock_host, mock_db)
      _search_indexes_mock.assert_awaited()
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_keys[0]))
      expect(rules).to(contain(mock_rule))
  
  @pytest.mark.asyncio
  async def test_get_all_entries(self, *args):
    with asynctest.patch.object(DB, 'fetch_members') as fetch_members_mock:
      mock_entry = {
        'rule_id': 'some-id',
        'host': 'some-host',
        'timeout': 1,
      }
      mock_keys = ['some-value']
      mock_db = MagicMock()
      mock_hgetall = CoroutineMock()
      mock_db.hgetall = mock_hgetall
      fetch_members_mock.return_value = mock_keys
      mock_hgetall.return_value = mock_entry
      entries = await RateLimiter.get_all_entries(mock_db)
      fetch_members_mock.assert_awaited()
      mock_hgetall.assert_awaited()
      expect(mock_hgetall.await_args[0][0]).to(equal(mock_keys[0]))
      expect(entries).to(contain(mock_entry))
    
  @pytest.mark.asyncio
  async def test_increment_entry_count(self, *args):
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hincrby = CoroutineMock()
    mock_db.hincrby = mock_hincrby
    await RateLimiter.increment_entry_count(mock_id, mock_db)
    mock_hincrby.assert_awaited_with(mock_id, 'count', 1)

  @pytest.mark.asyncio
  async def test_decrement_entry_count(self, *args):
    mock_id = 'some-value'
    mock_db = MagicMock()
    mock_hincrby = CoroutineMock()
    mock_db.hincrby = mock_hincrby
    await RateLimiter.decrement_entry_count(mock_id, mock_db)
    mock_hincrby.assert_awaited_with(mock_id, 'count', -1)
