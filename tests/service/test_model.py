import pytest
import asyncio
import mock
from mock import patch, MagicMock
from asynctest import CoroutineMock
from expects import expect, equal, raise_error, be_an, have_keys
from api.service import Service, service_validator
from api.util import Validate

class TestService:
  @pytest.mark.asyncio
  async def test_create(self, *args):
    with patch.object(service_validator, 'validate') as validate_mock:
      validate_mock.return_value = True
      mock_ctx = {}
      mock_db = MagicMock()
      mock_db.insert_one = CoroutineMock()
      await Service.create(mock_ctx, mock_db)
      mock_db.insert_one.assert_awaited_with(mock_ctx)
    
      try:
        validate_mock.return_value = False
        mock_ctx = {}
        mock_db = {}
        await Service.create(mock_ctx, mock_db)
      except Exception as err:
        expect(err.args[0]).to(be_an(object))
        expect(err.args[0]).to(have_keys('message', 'status_code'))
    
  @pytest.mark.asyncio
  async def test_update(self, *args):
    with patch.object(Validate, 'object_id') as validate_id_mock:
      with patch('bson.ObjectId') as bson_object_id_mock:
        with patch.object(service_validator, 'validate') as validate_mock:
          validate_mock.return_value = True
          bson_object_id_mock.return_value = True
          validate_id_mock.return_value = True
          mock_id = 'some-value'
          mock_ctx = {}
          mock_db = MagicMock()
          mock_db.update_one = CoroutineMock()

          await Service.update(mock_id, mock_ctx, mock_db)
          validate_id_mock.assert_called_with(mock_id)
          bson_object_id_mock.assert_called_with(mock_id)

          try:
            validate_mock.return_value = False
            await Service.update(mock_id, mock_ctx, mock_db)
          except Exception as err:
            expect(err.args[0]).to(have_keys('message', 'status_code'))
          
  @pytest.mark.asyncio
  async def test_get_by_id(self, *args):
    with patch('bson.ObjectId') as bson_object_id_mock:
      with patch.object(Validate, 'object_id') as validate_id_mock:
        bson_object_id_mock.return_value = True
        validate_id_mock.return_value = True
        
        mock_id = 'some-value'
        mock_db = MagicMock()
        mock_db.find_one = CoroutineMock()

        await Service.get_by_id(mock_id, mock_db)
        mock_db.find_one.assert_called()
        bson_object_id_mock.assert_called_with(mock_id)
        # expect(mock_db.find_one.call_args.args[0]).to(be_an(object))
        # expect(mock_db.find_one.await_args).to(equal('test')) #TODO: fix this test 
