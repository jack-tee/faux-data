from datafaker.utils import get_parts
import unittest


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
