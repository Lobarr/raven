import mock
from mock import patch, MagicMock
from expects import expect, equal, be_a

from api.util import Token


class TestToken:
    @patch('jwt.encode')
    def test_generate(self, *args):
        mock_payload = {}
        Token.generate(mock_payload)
        args[0].assert_called()
        expect(args[0].call_args.args[0]).to(equal(mock_payload))

    @patch('jwt.decode')
    def test_decode(self, *args):
        mock_token = 'some-value'
        Token.decode(mock_token)
        args[0].assert_called()
        expect(args[0].call_args.args[0]).to(equal(mock_token))
