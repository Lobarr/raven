from asynctest import CoroutineMock, patch as async_patch
from mock import patch

@patch('api.util.Token.decode')
def test_auth_middleware(*args):
  pass
