import mock
from mock import patch, MagicMock
from expects import expect, equal
from api.util.bson import Bson


class TestBson:
    @patch('bson.json_util.dumps')
    @patch('json.loads')
    def test_to_json(self, *args):
        mock_ctx = {}
        Bson.to_json(mock_ctx)
        args[0].assert_called()
        args[1].assert_called_with(mock_ctx)

    @patch('bson.ObjectId.is_valid')
    def test_validate_schema_id(self, *args):
        mock_field = 'some-field'
        mock_value = 'some-value'
        mock_error = MagicMock()
        args[0].return_value = False
        Bson.validate_schema_id(mock_field, mock_value, mock_error)
        args[0].assert_called_with(mock_value)
        expect(mock_error.call_args[0][0]).to(equal(mock_field))

        mock_error.reset_mock()
        args[0].return_value = True
        Bson.validate_schema_id(mock_field, mock_value, mock_error)
        mock_error.assert_not_called()
