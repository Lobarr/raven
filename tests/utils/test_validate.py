import mock
from mock import patch, MagicMock
from expects import expect, equal, be_a, have_keys

from api.util import Validate

class TestValidate:
  def test_object_id(self, *args):
    try:
      with patch('bson.ObjectId.is_valid') as is_valid_mock:
        is_valid_mock.return_value = False
        mock_id = 'some-value'
        Validate.object_id(mock_id)
    except Exception as err:
      expect(err.args[0]).to(be_a(object))
      expect(err.args[0]).to(have_keys('message', 'status_code'))
    
