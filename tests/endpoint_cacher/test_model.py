# import pytest
# import asynctest
# from api.service import Service
# from api.endpoint_cacher import EndpointCacher
# from mock import MagicMock
# from asynctest import CoroutineMock

# class TestEndpointCacher:
#   @pytest.mark.asyncio
#   async def test_create(self, *args):
#     with asynctest.patch.object(Service, 'check_exists') as check_exists_mock:
#       mock_ctx = {}
#       mock_db = MagicMock()
#       mock_db.insert_one = CoroutineMock()
#       await EndpointCacher.create(mock_ctx, mock_db, mock_db)
#       mock_db.insert_one.assert_awaited_with(mock_ctx)

#       mock_ctx = {
#         'service_id': 'some-value'
#       }
#       await EndpointCacher.create(mock_ctx, mock_db, mock_db)
#       check_exists_mock.assert_called()
