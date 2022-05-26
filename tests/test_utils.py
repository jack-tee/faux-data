import unittest

import pytest
from faux_data.utils import get_parts, split_gcs_path, extract_precision_and_scale


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


class TestUtilsSplitGcsPath(unittest.TestCase):

    def test_split_parts_with_gs_prefix(self):
        path = "gs://mybucket/some/path/file.csv"
        split_path = split_gcs_path(path)
        assert split_path.group("bucket") == "mybucket"
        assert split_path.group("obj") == "some/path/file.csv"

    def test_split_parts_with_no_prefix(self):
        path = "mybucket2/some/path/to/file.csv"
        split_path = split_gcs_path(path)
        assert split_path.group("bucket") == "mybucket2"
        assert split_path.group("obj") == "some/path/to/file.csv"

    def test_split_parts_invalid(self):
        path = "sometext"
        with pytest.raises(Exception) as e:
            split_path = split_gcs_path(path)
        assert "sometext" in repr(e)


class TestUtilsExtractPrecisionAndScale(unittest.TestCase):

    def test_extract_precision_and_scale(self):
        type_ = "Decimal(12,2)"
        precision, scale = extract_precision_and_scale(type_)
        assert precision == 12
        assert scale == 2

    def test_extract_precision_and_scale_invalid(self):
        type_ = "Decimal(12)"
        with pytest.raises(Exception) as e:
            precision, scale = extract_precision_and_scale(type_)
        assert type_ in repr(e)
