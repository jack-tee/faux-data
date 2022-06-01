from datetime import datetime
import unittest

import freezegun
import pytest
from faux_data.utils import *
from faux_data.template_rendering import resolve_time_period


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


class TestResolveTimePeriod:

    # yapf: disable
    test_values = [

        # default
        (None, None, datetime(2021, 2, 1), datetime(2021, 2, 2)),

        # just start provided
        ("2020-02-01", None, datetime(2020, 2, 1), datetime(2020, 2, 2)),
        ("+3H", None, datetime(2021, 2, 2, 18, 5, 6), datetime(2021, 2, 3, 18, 5, 6)),
        ("-4H", None, datetime(2021, 2, 2, 11, 5, 6), datetime(2021, 2, 2, 15, 5, 6)),

        # just end provided
        (None, "2020-02-01", datetime(2020, 1, 31), datetime(2020, 2, 1)),
        (None, "+8H", datetime(2021, 2, 2, 15, 5, 6), datetime(2021, 2, 2, 23, 5, 6)),
        (None, "-4H", datetime(2021, 2, 1, 11, 5, 6), datetime(2021, 2, 2, 11, 5, 6)),

        # both start and end provided
        ("2020-01-15", "2020-02-15", datetime(2020, 1, 15), datetime(2020, 2, 15)),
        ("2020-01-15", "+8H5min", datetime(2020, 1, 15), datetime(2020, 1, 15, 8, 5)),
        ("-4H4min", "2021-08-02 04:04:00", datetime(2021, 8, 2), datetime(2021, 8, 2, 4, 4)),
        ("2021-08-02 04:04:00", "10min", datetime(2021, 8, 2, 4, 4), datetime(2021, 8, 2, 4, 14)),
        ("-10min", "10min", datetime(2021, 2, 2, 14, 55, 6), datetime(2021, 2, 2, 15, 15, 6))
    ]

    @pytest.mark.parametrize("start,end,expected_start,expected_end", test_values)
    @freezegun.freeze_time("2021-02-02 15:05:06")
    def test_resolve_time_period(self, start, end, expected_start, expected_end):
        output_start, output_end = resolve_time_period(start, end)
        assert output_start == expected_start
        assert output_end == expected_end

    # yapf: enable


class TestNormalisePath:
    # yapf: disable
    test_values = [
        ("gs://mybucket/myfile.csv", "gs://mybucket/myfile.csv"),
        ("gs://mybucket//myfile.csv", "gs://mybucket/myfile.csv"),
        ("gs://mybucket/somedir/../myfile.csv", "gs://mybucket/myfile.csv"),
        ("gs://mybucket/somedir/./myfile.csv", "gs://mybucket/somedir/myfile.csv"),
        ("/some/absolute/path/myfile.csv", "/some/absolute/path/myfile.csv"),
        ("relative/path/file.csv", "relative/path/file.csv"),
    ]

    @pytest.mark.parametrize("path,normalised_path", test_values)
    def test_path(self, path, normalised_path):
        assert normalise_path(path) == normalised_path

    # yapf: enable