import mock
from mock import patch, MagicMock
from expects import expect, equal, be_a

from api.util import Password

class TestPassword:
  @patch('bcrypt.gensalt')
  @patch('bcrypt.hashpw')
  def test_hash(self, *args):
    mock_password = 'some-value'
    Password.hash(mock_password)
    args[0].assert_called()
    args[1].assert_called()
  
  @patch('bcrypt.checkpw')
  def test_validate(self, *args):
    mock_password = MagicMock()
    mock_hash = MagicMock()
    Password.validate(mock_password, mock_hash)
    args[0].assert_called()
    mock_hash.encode.assert_called()
    mock_password.encode.assert_called()
