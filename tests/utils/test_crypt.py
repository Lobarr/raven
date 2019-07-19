import mock
from mock import patch, MagicMock
from cryptography.exceptions import InvalidSignature
from expects import expect, equal, be_an, be_a, have_keys, be_true, be_false

from api.util import Crypt, Bytes

class TestCrypt:
  @patch('cryptography.hazmat.primitives.asymmetric.ec.generate_private_key')
  def test_generate_key_pair(self, *args):
    keys = Crypt.generate_key_pair()
    args[0].assert_called()
    expect(keys).to(be_an(object))
    expect(keys).to(have_keys('private_key', 'public_key'))

  @patch.object(Bytes, 'encode_bytes')
  @patch.object(Bytes, 'object_to_bytes')
  @patch('cryptography.hazmat.primitives.serialization.load_pem_private_key')
  def test_sign(self, *args):
    mock_object = {}
    mock_private = ''
    signature = Crypt.sign(mock_object, mock_private)
    args[0].assert_called()
    args[1].assert_called_with(mock_object)
    args[2].assert_called()

  @patch.object(Bytes, 'decode_bytes')
  @patch.object(Bytes, 'object_to_bytes')
  def test_verify(self, *args):

    with patch('cryptography.hazmat.primitives.serialization.load_pem_public_key') as load_public_key_mock:
      mock_message = {}
      mock_signature = 'some-value'
      mock_public_key = 'some-value'
      verified = Crypt.verify(mock_message, mock_signature, mock_public_key)
      load_public_key_mock.assert_called()
      args[0].assert_called_with(mock_message)
      args[1].assert_called()
      expect(verified).to(be_true)
    
    with patch('cryptography.hazmat.primitives.serialization.load_pem_public_key') as load_public_key_mock:
      load_public_key_mock.side_effect = InvalidSignature()
      mock_message = {}
      mock_signature = 'some-value'
      mock_public_key = 'some-value'
      verified = Crypt.verify(mock_message, mock_signature, mock_public_key)
      expect(verified).to(be_false)
  


 