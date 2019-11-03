import mock
from mock import patch, MagicMock
from expects import expect, equal

from api.util.bytes import Bytes


class TestBytes:
    def test_str_to_bytes(self, *args):
        mock_str = MagicMock()
        Bytes.str_to_bytes(mock_str)
        mock_str.encode.assert_called()

    def test_object_to_bytes(self, *args):
        with patch('json.dumps') as json_dumps_mock:
            mock_obj = MagicMock()
            mock_encode = MagicMock()
            Bytes.object_to_bytes(mock_obj)
            json_dumps_mock.assert_called_with(mock_obj)

    @patch('base64.b64encode')
    def test_encode_bytes(self, *args):
        mock_data = {}
        Bytes.encode_bytes(mock_data)
        args[0].assert_called_with(mock_data)

    @patch('base64.b64decode')
    def test_decode_bytes(self, *args):
        mock_data = {}
        Bytes.decode_bytes(mock_data)
        args[0].assert_called_with(mock_data)
