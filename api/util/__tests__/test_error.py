import mock
from mock import patch, MagicMock
from expects import expect, equal

from api.util import Error


class TestError:
    @patch('aiohttp.web.json_response')
    def test_handle(self, *args):
        with patch('pydash.has') as has_mock:
            has_mock.return_value = True
            mock_exception_ctx = {
                'message': 'test',
                'status_code': 200
            }
            mock_exception = Exception(mock_exception_ctx)
            Error.handle(mock_exception)
            has_mock.assert_called()
            args[0].assert_called_with(
                mock_exception_ctx, status=mock_exception_ctx['status_code'])

        with patch('pydash.has') as has_mock:
            has_mock.return_value = False
            mock_exception_ctx = 'some-error'
            mock_exception = Exception(mock_exception_ctx)
            Error.handle(mock_exception)
            args[0].assert_called()
            expect(args[0].call_args.args[0]['message']).to(
                equal(mock_exception_ctx))
