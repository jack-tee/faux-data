import unittest

from datafaker.utils import get_parts


class TestUtilsGetArgs(unittest.TestCase):
    # Fixed Column
    def test_get_parts_5_args(self):
        parts = get_parts("mycol Random String 5 6")
        assert len(parts) == 5

    def test_get_parts_2_args(self):
        parts = get_parts("mycol Random")
        assert len(parts) == 2
        assert parts == ["mycol", "Random"]

    def test_get_parts_double_space(self):
        parts = get_parts("mycol  Random")
        assert len(parts) == 2
        assert parts == ["mycol", "Random"]

    def test_get_parts_trailing_spaces(self):
        parts = get_parts("mycol  Random Int  ")
        assert len(parts) == 3
        assert parts == ["mycol", "Random", "Int"]

    def test_get_parts_value_with_space_single_quotes(self):
        parts = get_parts("mycol Fixed String 'boop boop'")
        assert len(parts) == 4
        assert parts == ["mycol", "Fixed", "String", "boop boop"]

    def test_get_parts_value_with_space_double_quotes(self):
        parts = get_parts(
            'mycol Random Timestamp "2021-04-03 06:02:03" 2021-05-02')
        assert len(parts) == 5
        assert parts == [
            "mycol", "Random", "Timestamp", "2021-04-03 06:02:03", "2021-05-02"
        ]
