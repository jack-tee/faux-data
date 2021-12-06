import pandas as pd

import pytest
import unittest

from datafaker.column import Column, ColumnGenerationException
from datafaker import column
from datafaker.table import Table, TableParsingException

from tests.utils import empty_df

pd.set_option('max_colwidth', 800)


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
        assert all(tbl.df[["col1", "col2", "col3"]].notnull().sum(axis=1) == 1)


class TestArrayColumnGeneration(unittest.TestCase):
    def test_basic_array_column(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Fixed Int 4
          - col: col2 Fixed Int 5
          - col: arr_col Array
            source_columns:
              - col1
              - col2
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 3

        first_row = tbl.df['arr_col'][0]
        assert list(first_row) == [4, 5]


class TestSequentialColumnGeneration(unittest.TestCase):
    def test_basic_seq_column(self):
        conf = """
        name: mytbl
        rows: 5
        columns:
          - col: seq_col Sequential Int 10 3
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert list(tbl.df['seq_col'].values) == [10, 13, 16, 19, 22]

    def test_basic_seq_column_timestamp(self):
        conf = """
        name: mytbl
        rows: 5
        columns:
          - col: seq_col Sequential Timestamp "1999-12-31 23:58:00" "1min1S"
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        print(tbl.df['seq_col'].values)
        assert list(tbl.df['seq_col'].values) == [
            pd.Timestamp('1999-12-31T23:58:00.000000000'),
            pd.Timestamp('1999-12-31T23:59:01.000000000'),
            pd.Timestamp('2000-01-01T00:00:02.000000000'),
            pd.Timestamp('2000-01-01T00:01:03.000000000'),
            pd.Timestamp('2000-01-01T00:02:04.000000000')
        ]


class TestEmptyColumn(unittest.TestCase):
    def test_basic_empty(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Empty String
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert all(tbl.df["col1"].isnull())
        assert tbl.df["col1"].dtype == "string"

    def test_basic_empty_int(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Empty Int
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert all(tbl.df["col1"].isnull())
        assert tbl.df["col1"].dtype == "Int64"


class TestNestedColumns(unittest.TestCase):
    def test_basic_nested_table(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: payload Map
            columns:
              - col: num Random Int 0 10
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert tbl.df.columns == ["payload"]

    def test_basic_multi_level_nested_table(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: message_body Map
            columns:

              - col: schema Map
                columns:
                  - col: type Fixed String struct

              - col: payload Map
                columns:
                  - col: user Map
                    columns:
                    - col: id Random id 1 200
                    - col: email Random String 4 8

        """
        tbl = Table.parse_from_yaml(conf)

        assert len(tbl.columns) == 1
        assert isinstance(tbl.columns[0], column.Map)
