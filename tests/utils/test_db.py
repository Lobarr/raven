import mock
from mock import MagicMock
from expects import expect, equal

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
