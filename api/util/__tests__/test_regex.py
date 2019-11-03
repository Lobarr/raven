import mock
from mock import patch
from expects import expect, equal

from api.util import Regex


class TestRegex:
    def test_best_match(self, *args):
        mock_entities = [
            {
                'regex_groups': (0, 0, 0)
            }
        ]
        best_path = Regex.best_match(mock_entities)
        expect(best_path).to(equal(mock_entities[0]))

        mock_entities = []
        best_path = Regex.best_match(mock_entities)
        expect(best_path).to(equal(None))

    def test_get_matched_paths(self, *args):
        pass
