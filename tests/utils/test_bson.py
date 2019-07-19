import mock
from mock import patch
from expects import expect, equal

from api.util.bson import Bson

class TestBson:
  @patch('bson.json_util.dumps')
  @patch('json.loads')
  def test_to_json(self, *args):
    mock_ctx = {}
    Bson.to_json(mock_ctx)
    args[0].assert_called()
    args[1].assert_called_with(mock_ctx)
