import unittest

import numpy as np
import pandas as pd
import pytest
from datafaker import column
from datafaker.column import ColumnGenerationException
from datafaker.factory import ColumnFactory

from tests.utils import empty_df


class TestColumnParsing(unittest.TestCase):
    # Fixed Column
    def test_fixed_column_parses(self):
        conf = """
        name: mycol
        column_type: Fixed
        value: b
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

    def test_short_fixed_column_parses(self):
        conf = """
        col: mycol Fixed String b
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

    def test_short_fixed_column_parses_with_spaced_value(self):
        conf = """
        col: mycol Fixed String 'boop boop'
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)
        assert col.value == "boop boop"

    # Random Column
    def test_random_column_parses(self):
        conf = """
        name: mycol
        column_type: Random
        min: 1
        max: 5
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)
        assert col.data_type == "Int"
        assert col.min == 1
        assert col.max == 5

    def test_short_random_column_parses(self):
        conf = """
        col: mycol Random Int 2 6
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)
        assert col.data_type == "Int"
        assert col.min == "2"
        assert col.max == "6"

    # Selection Column
    def test_selection_column_parses(self):
        conf = """
        name: mycol
        column_type: Selection
        values:
          - a
          - b
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Selection)
        assert col.data_type == None

    def test_short_selection_column_parses(self):
        conf = """
        col: mycol Selection
        values:
          - g
          - h
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Selection)

    def test_short_selection_column_int_parses(self):
        conf = """
        col: mycol Selection Int
        values:
          - 4
          - 5
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Selection)
        assert col.data_type == 'Int'

    # Map Column
    def test_short_map(self):
        conf = """
        col: mycol Map
        source_columns:
          - col1
          - col2
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Map)
        assert col.source_columns == ["col1", "col2"]

    def test_long_map(self):
        conf = """
        name: mycol
        column_type: Map
        source_columns:
          - col3
          - col4
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Map)
        assert col.source_columns == ["col3", "col4"]

    # Sequential Column
    def test_short_sequential(self):
        conf = """
        col: mycol Sequential Timestamp 10 3
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Sequential)
        assert int(col.start) == 10
        assert int(col.step) == 3

    def test_short_sequential_dates(self):
        conf = """
        col: mycol Sequential Timestamp "2021-03-02 00:06:02" -2H30m
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Sequential)
        assert col.start == "2021-03-02 00:06:02"
        assert col.step == "-2H30m"

    def test_long_sequential_defaults(self):
        conf = """
        name: mycol
        column_type: Sequential
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Sequential)
        assert col.start == 0
        assert col.step == 1

    def test_long_sequential_y2kbug(self):
        conf = """
        name: mycol
        column_type: Sequential
        data_type: Timestamp
        start: "1999-12-31 23:50:00" 
        step: "1min1S"
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Sequential)
        assert col.start == "1999-12-31 23:50:00"
        assert col.step == "1min1S"

    # Empty Column
    def test_empty_short(self):
        conf = """
        col: mycol Empty String
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Empty)
        assert col.data_type == "String"

    def test_empty_long(self):
        conf = """
        name: mycol 
        column_type: Empty
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Empty)
        assert col.data_type == None

    # MapValues Column
    def test_map_values_short(self):
        conf = """
        col: mycol MapValues String
        source_column: someother
        values:
          a: 4
          b: boop
          c: foo
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.MapValues)
        assert col.data_type == "String"
        assert col.values == {"a": 4, "b": "boop", "c": "foo"}
        assert np.isnan(col.default)

    def test_map_values_long(self):
        conf = """
        name: mycol
        column_type: MapValues
        source_column: someother
        default: bar
        values:
          a: "yo"
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.MapValues)
        assert col.data_type is None
        assert col.values == {"a": "yo"}
        assert col.default == "bar"


class TestFixedColumnGeneration(unittest.TestCase):
    def test_fixed_column_plain_string(self):
        conf = """
        name: mycol
        column_type: Fixed
        value: b
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

        series = col.generate(5)
        assert series.size == 5
        assert all(series == "b")
        assert series.dtype == 'object'

    def test_fixed_column_int_string(self):
        conf = """
        name: mycol
        column_type: Fixed
        value: '4'
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

        series = col.generate(5)
        assert series.size == 5
        assert all(series == "4")
        assert series.dtype == 'object'

    def test_fixed_column_int(self):
        conf = """
        name: mycol
        column_type: Fixed
        value: 4
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

        series = col.generate(5)
        assert series.size == 5
        assert all(series == 4)
        assert pd.api.types.is_integer_dtype(series)

    def test_fixed_column_int_short(self):
        conf = """
        col: mycol Fixed Int 3
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

        series = col.generate(5)
        assert all(series == 3)
        assert series.dtype == 'Int64'

    def test_fixed_column_float_short(self):
        conf = """
        col: mycol Fixed Float 3.56
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

        series = col.generate(5)
        assert all(series == 3.56)
        assert series.dtype == 'float64'

    def test_fixed_column_float_long(self):
        conf = """
        name: mycol
        column_type: Fixed 
        value: 3.76
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Fixed)

        series = col.generate(5)
        assert all(series == 3.76)
        assert series.dtype == 'float64'


class TestRandomColumnGeneration(unittest.TestCase):
    def test_random_column_no_data_type(self):
        conf = """
        name: mycol
        column_type: Random
        min: 1
        max: 10
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(20)
        assert series.dtype == 'Int64'

    def test_random_column_between_min_max(self):
        conf = """
        name: mycol
        column_type: Random
        min: 5
        max: 8
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(50)

        assert series.size == 50
        # with 50 elements and only 4 possible values we should find some at the min and max value
        assert all(series[(series <= 8) & (series >= 5)])
        assert any(series == 8)
        assert any(series == 5)

    def test_error_random_column_invalid_min(self):
        conf = """
        name: mycol
        column_type: Random
        min: y
        max: 10
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        with pytest.raises(ColumnGenerationException) as e:
            col.maybe_add_column(empty_df())

        assert "mycol" in e.__repr__()
        assert "invalid literal for int" in e.__repr__()

    def test_random_float(self):
        conf = """
        name: mycol
        column_type: Random
        data_type: Float
        min: 1.23
        max: 3.45
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(10)

        assert all(series[(series <= 3.45) & (series >= 1.23)])

    def test_random_string(self):
        conf = """
        name: mycol
        column_type: Random
        data_type: String
        min: 8
        max: 14
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(100)

        lens = series.str.len()
        assert series.dtype == 'string'
        assert all((lens >= 8) & (lens <= 14))
        assert min(lens) == 8
        assert max(lens) == 14

    def test_random_string_short(self):
        conf = """
        col: mycol Random String 12 18
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(10)

        lens = series.str.len()
        assert series.dtype == 'string'
        assert all((lens >= 12) & (lens <= 18))

    def test_random_string_limited_to_5000_chars(self):
        conf = """
        col: mycol Random String 10000 100000
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(10)

        lens = series.str.len()
        assert series.dtype == 'string'
        assert all(lens == 5000)

    def test_random_timestamp_default_ms(self):
        conf = """
        col: mycol Random Timestamp '2021-01-01' "2021-04-01 12:00:00"
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(10)
        assert series.dtype == 'datetime64[ns]'
        assert all((series >= '2021-01-01')
                   & (series <= '2021-04-01 12:00:00'))

        # verify precision
        assert col.time_unit == 'ms'
        assert any(series.dt.second > 0)
        # microseconds return 6 digit number of millis and micros
        # mod 1000 to just get micros which should all be zero
        assert all(series.dt.microsecond.mod(1000) == 0)

    def test_random_timestamp_microsecond_prec(self):
        conf = """
        col: mycol Random Timestamp '2021-01-01 08:00:00' "2021-01-01 16:00:00"
        time_unit: us
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(10)
        assert series.dtype == 'datetime64[ns]'
        assert all((series >= '2021-01-01 08:00:00')
                   & (series <= '2021-01-01 16:00:00'))

        # verify precision
        assert col.time_unit == 'us'
        assert any(series.dt.microsecond > 0)
        assert all(series.dt.nanosecond == 0)

    def test_random_timestamp_second_prec(self):
        conf = """
        col: mycol Random Timestamp '2021-01-01 08:00:00' "2021-01-01 16:00:00"
        time_unit: s
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Random)

        series = col.generate(10)
        assert series.dtype == 'datetime64[ns]'
        assert all((series >= '2021-01-01 08:00:00')
                   & (series <= '2021-01-01 16:00:00'))

        # verify precision
        assert col.time_unit == 's'
        assert any(series.dt.second > 0)
        assert all(series.dt.microsecond == 0)


class TestSelectionColumnGeneration(unittest.TestCase):
    def test_selection_column_values(self):
        conf = """
        name: mycol
        column_type: Selection
        values:
          - a
          - b
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Selection)

        series = col.generate(10)
        assert series.size == 10
        assert all(series.isin(["a", "b"]))
        # should have both values in the output
        assert any(series == "a")
        assert any(series == "b")

    def test_selection_column_values_ints(self):
        conf = """
        name: mycol
        column_type: Selection
        data_type: Int
        values:
          - 3
          - 6
        """
        col = ColumnFactory.parse_from_yaml(conf)
        assert isinstance(col, column.Selection)

        series = col.generate(10)
        assert series.size == 10
        assert all(series.isin([3, 6]))
        # should have both values in the output
        assert any(series == 3)
        assert any(series == 6)
