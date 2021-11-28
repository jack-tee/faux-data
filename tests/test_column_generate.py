import pandas as pd

import pytest
import unittest

from datafaker.column import Column, ColumnGenerationException
from datafaker import columns
from datafaker.table import Table

from tests.utils import empty_df


class TestColumnParsing(unittest.TestCase):
    # Fixed Column
    def test_fixed_column_parses(self):
        conf = """
        name: mycol
        column_type: Fixed
        value: b
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)

    def test_short_fixed_column_parses(self):
        conf = """
        col: mycol Fixed String b
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)

    def test_short_fixed_column_parses_with_spaced_value(self):
        conf = """
        col: mycol Fixed String 'boop boop'
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)
        assert col.value == "boop boop"

    # Random Column
    def test_random_column_parses(self):
        conf = """
        name: mycol
        column_type: Random
        min: 1
        max: 5
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Random)
        assert col.data_type == "Int"
        assert col.min == 1
        assert col.max == 5

    def test_short_random_column_parses(self):
        conf = """
        col: mycol Random Int 2 6
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Random)
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
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Selection)
        assert col.data_type == None

    def test_short_selection_column_parses(self):
        conf = """
        col: mycol Selection
        values:
          - g
          - h
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Selection)

    def test_short_selection_column_int_parses(self):
        conf = """
        col: mycol Selection Int
        values:
          - 4
          - 5
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Selection)
        assert col.data_type == 'Int'

    # Map Column
    def test_short_map(self):
        conf = """
        col: mycol Map
        source_columns:
          - col1
          - col2
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Map)
        assert col.source_columns == ["col1", "col2"]

    def test_long_map(self):
        conf = """
        name: mycol
        column_type: Map
        source_columns:
          - col3
          - col4
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Map)
        assert col.source_columns == ["col3", "col4"]


class TestFixedColumnGeneration(unittest.TestCase):
    def test_fixed_column_plain_string(self):
        conf = """
        name: mycol
        column_type: Fixed
        value: b
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)

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
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)

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
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)

        series = col.generate(5)
        assert series.size == 5
        assert all(series == 4)
        assert pd.api.types.is_integer_dtype(series)

    def test_fixed_column_int_short(self):
        conf = """
        col: mycol Fixed Int 3
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Fixed)

        series = col.generate(5)
        assert all(series == 3)
        assert series.dtype == 'int64'


class TestRandomColumnGeneration(unittest.TestCase):
    def test_random_column_no_data_type(self):
        conf = """
        name: mycol
        column_type: Random
        min: 1
        max: 10
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Random)

        series = col.generate(20)
        assert series.dtype == 'int64'

    def test_random_column_between_min_max(self):
        conf = """
        name: mycol
        column_type: Random
        min: 5
        max: 8
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Random)

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
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Random)

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
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Random)

        series = col.generate(10)

        assert all(series[(series <= 3.45) & (series >= 1.23)])


class TestSelectionColumnGeneration(unittest.TestCase):
    def test_selection_column_values(self):
        conf = """
        name: mycol
        column_type: Selection
        values:
          - a
          - b
        """
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Selection)

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
        col = Column.parse_from_yaml(conf)
        assert isinstance(col, columns.Selection)

        series = col.generate(10)
        assert series.size == 10
        assert all(series.isin([3, 6]))
        # should have both values in the output
        assert any(series == 3)
        assert any(series == 6)
