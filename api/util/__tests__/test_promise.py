import pytest
import asynctest
from mock import MagicMock
from asynctest import CoroutineMock
from api.util import Async


class TestAsync:
    @pytest.mark.asyncio
    async def test_all(self, *args):
        with asynctest.patch('asyncio.gather', new=CoroutineMock()) as gather_mock:
            mock_coroutines = []
            await Async.all(mock_coroutines)
            gather_mock.assert_awaited()
