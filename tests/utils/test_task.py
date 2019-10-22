from mock import patch, MagicMock
from expects import expect, be_true, be_false, equal

from api.util.tasks import arg_needs_resource, get_mongo_collection, is_supported_func, map_args_to_resources

def test_args_needs_resource():
  mock_resource = 'some-resource'
  mock_arg = f'{mock_resource}:something'
  expect(arg_needs_resource(mock_arg, mock_resource)).to(be_true)

  mock_arg = 'something'
  expect(arg_needs_resource(mock_arg, mock_resource)).to(be_false)


def test_get_mongo_collection():
  mock_collection = 'some-collection'
  mock_arg = f'resource:{mock_collection}'
  expect(get_mongo_collection(mock_arg)).to(equal(mock_collection))

def test_is_supported_func():
  mock_func = 'some-func'
  mock_funcs = {}
  expect(is_supported_func(mock_func, mock_funcs)).to(be_false)

  mock_funcs[mock_func] = {}
  expect(is_supported_func(mock_func, mock_funcs)).to(be_true)

@patch('api.util.tasks.arg_needs_resource')
@patch('api.util.tasks.get_mongo_collection')
def test_map_args_to_resources(*args):
  mock_collection = 'some-collection'
  mock_args = ['mongo', 'redis']
  mock_resources = {
    'mongo': {
      mock_collection: {}
    },
    'redis': {}
  }
  args[0].return_value = mock_collection
  args[1].return_value = True
  mapped_args = map_args_to_resources(mock_args, mock_resources)

  args[1].assert_called()
  args[0].assert_called()
  expect(mapped_args).to(equal([{}, {}]))

  args[1].return_value = False
  mock_args = ['something']
  mapped_args = map_args_to_resources(mock_args, mock_resources)
  expect(mapped_args).to(equal(mock_args))



