import asyncio
import asynctest
import mock
import pytest
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal

from api.util.api import Api, Async

class TestApi:
  @pytest.mark.asyncio
  async def test_call(self, *args):
    with asynctest.mock.patch('aiohttp.request', create=True) as aiohttp_req_mock:
      mock_req = CoroutineMock()
      mock_req.__aexit__ = CoroutineMock()
      mock_req.__aenter__ = CoroutineMock()
      aiohttp_req_mock.return_value = mock_req
      expected_method = 'some-value'
      expected_url = 'some-value'
      expected_params = {}
      expected_data = {}
      expected_json = {}
      expected_cookies = {}
      expected_headers = {}
      expected_auth = {}
      await Api.call(method=expected_method, url=expected_url, params=expected_params, data=expected_data, json=expected_json, cookies=expected_cookies, headers=expected_headers, auth=expected_auth)
      aiohttp_req_mock.assert_called_with(method=expected_method, url=expected_url, params=expected_params, data=expected_data, json=expected_json, cookies=expected_cookies, headers=expected_headers, auth=expected_auth)
  
  @pytest.mark.asyncio
  async def test_batch(self, *args):
    with asynctest.mock.patch.object(Api, 'call') as call_mock:
      expected_requests = [
        {
          'method': 'some-value',
          'url': 'some-value',
          'params': {},
          'data': {},
          'json': {},
          'cookies': {},
          'headers': {},
          'auth': {}
        },
        {
          'method': 'some-value',
          'url': 'some-value',
          'params': {},
          'data': {},
          'json': {},
          'cookies': {},
          'headers': {},
          'auth': {}
        },
        {
          'method': 'some-value',
          'url': 'some-value',
          'params': {},
          'data': {},
          'json': {},
          'cookies': {},
          'headers': {},
          'auth': {}
        }
      ]
      res = await Api.batch(expected_requests)
      expect(call_mock.call_count).to(equal(len(expected_requests)))
      expect(len(res)).to(equal(len(expected_requests)))
  
  @pytest.mark.asyncio
  @asynctest.patch.object(Async, 'all')
  @asynctest.patch.object(Api, 'call')
  async def test_batch_async(self, *args):
    # with  as call_mock:
    expected_requests = [
      {
        'method': 'some-value',
        'url': 'some-value',
        'params': {},
        'data': {},
        'json': {},
        'cookies': {},
        'headers': {},
        'auth': {}
      },
      {
        'method': 'some-value',
        'url': 'some-value',
        'params': {},
        'data': {},
        'json': {},
        'cookies': {},
        'headers': {},
        'auth': {}
      },
      {
        'method': 'some-value',
        'url': 'some-value',
        'params': {},
        'data': {},
        'json': {},
        'cookies': {},
        'headers': {},
        'auth': {}
      }
    ]
    res = await Api.batch_async(expected_requests)
    expect(args[0].call_count).to(equal(len(expected_requests)))
    args[1].assert_called()
