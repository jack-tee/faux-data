import pandas as pd

import pytest
import unittest

from datafaker.column import Column, ColumnGenerationException
from datafaker import column
from datafaker.table import Table

from tests.utils import empty_df


class TestMapColumnGeneration(unittest.TestCase):
    def test_basic_map_column(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Fixed String 'boo'
          - col: col2 Fixed Int 5
          - col: map_col Map
            source_columns:
              - col1
              - col2
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 3

        example_dict = tbl.df['map_col'][0]
        assert example_dict == {'col1': 'boo', 'col2': 5}

    def test_basic_map_column_drop_source(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Fixed String 'boo'
          - col: col2 Fixed Int 5
          - col: map_col Map
            source_columns:
              - col1
              - col2
            drop: True
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert tbl.df.columns == ["map_col"]

    def test_basic_map_column_with_select_one(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Fixed String 'boo'
          - col: col2 Fixed Int 5
          - col: col3 Fixed Float 5.6
          - col: map_col Map
            source_columns: [col1, col2, col3]
            select_one: True
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        print(tbl.df)

        # check that the source_columns only have one non-null
        assert all(tbl.df[["col1", "col2", "col3"]].notnull().sum(axis=1))


class TestNestedColumns(unittest.TestCase):
    @pytest.mark.skip(reason="Not implemented yet")
    def test_basic_nested_table(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: payload.col1 Fixed String 'boo'
          - col: payload.col2.a Fixed Int 5
          - col: payload.col2.b Fixed String yope
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert tbl.df.columns == ["payload"]