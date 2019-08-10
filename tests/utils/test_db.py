import mock
import pytest
from asynctest import CoroutineMock
from mock import MagicMock, patch
from expects import expect, equal, be_a

from api.util.db import DB

class TestDB:
  def test_get(self, *args):
    mock_table = 'some-table'
    mock_request = MagicMock()
    mock_request.app = {
      'mongo': {
        (mock_table): mock_table
      }
    }

    expect(DB.get(mock_request, mock_table)).to(equal(mock_table))

  def test_get_redis(self, *args):
    mock_redis = {}
    mock_request = MagicMock()
    mock_request.app = {
      'redis': mock_redis
    }
    expect(DB.get_redis(mock_request)).to(equal(mock_redis))

  @patch('pydash.omit')
  def test_format_document(self, *args):
    mock_document = {
      '_id': {
        '$oid': 'some-value'
        }
    }
    args[0].return_value = {}
    formatted = DB.format_document(mock_document)
    args[0].assert_called_with(mock_document, '_id')
    expect(formatted['_id']).to(equal(mock_document['_id']['$oid']))
  
  @patch.object(DB, 'format_document')
  def test_format_documents(self, *args):
    mock_documents = [
      {
        '_id': {
          '$oid': 'some-value'
        }
      },
      {
        '_id': {
          '$oid': 'some-value'
        }
      }
    ]
    formatted = DB.format_documents(mock_documents)
    expect(args[0].call_count).to(equal(len(mock_documents)))
    expect(formatted).to(be_a(list))
  
  @pytest.mark.asyncio
  async def test_fetch_members(self, *args):
    mock_db = CoroutineMock()
    mock_db.smembers = CoroutineMock()
    mock_key = 'some-value'
    await DB.fetch_members(mock_key, mock_db)
    mock_db.smembers.assert_called_with(mock_key, encoding='utf-8')
