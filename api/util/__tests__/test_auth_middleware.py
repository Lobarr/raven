import pytest
from pydash import omit
from expects import expect, raise_error, equal
from asynctest import CoroutineMock, patch as async_patch
from mock import patch, MagicMock
from api.admin import AdminDTO
from api.util.auth_middleware import auth_middleware
from api.util import Error

@pytest.mark.asyncio
async def test_auth_middleware():
  with patch('api.util.Error.handle') as handle_mock:
    with patch('api.util.Token.decode') as decode_mock:
      with async_patch('api.admin.service.Admin.get_by_id') as get_by_id_mock:
        mock_handler = CoroutineMock()
        mock_request = MagicMock()
        mock_id = 'some-id'
        mock_token = "some-token"
        mock_token_context = {
          '_id': mock_id,
        }
        mock_admin = AdminDTO()
        mock_admin.id = mock_id
        mock_admin.token = mock_token
        
        #? should handle login route 
        mock_request.path_qs = "/admin/login"
        await auth_middleware(mock_request, mock_handler)
        mock_handler.assert_awaited()

        #? should handle empty token
        mock_request.path_qs = "*"
        await auth_middleware(mock_request, mock_handler)
        handle_mock.assert_called()

        #? should handle valid token
        decode_mock.return_value = mock_token_context
        get_by_id_mock.return_value = mock_admin
        mock_request.headers.get.return_value = mock_token
        
        await auth_middleware(mock_request, mock_handler)
        decode_mock.assert_called()
        expect(get_by_id_mock.await_args[0][0]).to(equal(mock_token_context['_id']))
        mock_handler.assert_awaited()

        #? should handle invalid token
        mock_admin.token = None
        get_by_id_mock.return_value = mock_admin
        
        await auth_middleware(mock_request, mock_handler)
        handle_mock.assert_called()
