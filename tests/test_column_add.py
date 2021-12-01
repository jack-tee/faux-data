import pandas as pd

import pytest
import unittest

from datafaker.column import Column, ColumnGenerationException
from datafaker import columns
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

    def test_basic_map_column_with_parent(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Fixed String 'boo'
          - col: col2 Fixed Int 5
          - col: map_col Map
            parent: 1
            source_columns:
              - col1
              - col2
            drop: True
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert tbl.df.columns == ["map_col"]

        example_dict = tbl.df['map_col'][0]
        assert example_dict == {1: {'col1': 'boo', 'col2': 5}}


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