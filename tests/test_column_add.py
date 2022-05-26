import unittest

import pandas as pd
import numpy as np
import pytest
from faux_data import column
from faux_data.table import Table

pd.set_option('max_colwidth', 800)


class TestOutputTypes(unittest.TestCase):

    def test_random_ints_output_as_strings(self):
        """Tests that a random int column can be output as string."""

        conf = """
        name: mytbl
        rows: 5
        columns:
          - col: tcol Random Int 3 10
            output_type: String
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 1
        assert tbl.df["tcol"].dtype == 'string'

    def test_random_timestamps_output_as_strings_default_format(self):
        """Tests that a random timestamp column can be output as string."""

        conf = """
        name: mytbl
        rows: 5
        columns:
          - col: tcol Random Timestamp "2021-01-01" "2021-01-02 23:59:59"
            output_type: String
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        # print(tbl.df)
        # print(tbl.df.dtypes)
        assert len(tbl.df.columns) == 1
        assert tbl.df["tcol"].dtype == 'string'
        # check the dates are in the correct format
        assert all(tbl.df["tcol"].str.fullmatch(
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"))

    def test_random_timestamps_output_as_strings_custom_format(self):
        """Tests that a random timestamp column can be output as string with a custom date_format."""

        conf = """
        name: mytbl
        rows: 5
        columns:
          - col: tcol Random Timestamp "2021-01-01" "2021-10-02 23:59:59"
            output_type: String
            date_format: "%Y-%m-01"
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        # print(tbl.df)
        # print(tbl.df.dtypes)
        assert len(tbl.df.columns) == 1
        assert tbl.df["tcol"].dtype == 'string'
        # check the dates are in the correct format
        assert all(tbl.df["tcol"].str.fullmatch(r"\d{4}-\d{2}-01"))


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

    def test_basic_map_column_with_json(self):
        conf = """
        name: mytbl
        rows: 12
        columns:
          - col: map_col Map
            json: True
            drop: True
            columns:
              - col: col1 Fixed String 'boo'
              - col: col2 Fixed Int 5
              - col: col3 Fixed Float 5.6

        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        assert len(tbl.df) == 12
        assert tbl.df["map_col"][0] == """{"col1":"boo","col2":5,"col3":5.6}"""
        assert tbl.df["map_col"].dtype == "string"


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
        assert len(tbl.df.columns) == 1

        first_row = tbl.df['arr_col'][0]
        assert list(first_row) == [4, 5]

    def test_basic_array_column_no_drop(self):
        """When `drop: False` is set the source columns should be left in the output"""
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: col1 Fixed Int 4
          - col: col2 Fixed Int 5
          - col: arr_col Array
            drop: False
            source_columns:
              - col1
              - col2
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        #print(tbl.df)
        assert len(tbl.df.columns) == 3

    def test_array_column_drop_nulls(self):
        """When `drop_nulls: True` is set the null values should be removed from the array"""
        conf = """
        name: mytbl
        rows: 100
        columns:
          - col: col1 Fixed String foo
            null_percentage: 50
          - col: col2 Fixed String bar
            null_percentage: 50
          - col: arr_col Array
            drop_nulls: True
            source_columns:
              - col1
              - col2
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        c = tbl.df["arr_col"]

        # check the arrays are of the correct lengths
        assert all(c.apply(lambda x: x.size).isin([0, 1, 2]))

        # This doesn't work because it doesn't seem to interpret the arrays properly
        # assert all(tbl.df['arr_col'].isin([
        #     np.empty(0, dtype=object),
        #     np.array(['foo']),
        #     np.array(['bar']),
        #     np.array(['foo', 'bar'])
        # ]))
        # so convert them to strings and check those

        assert all(
            c.astype(str).isin(['[]', "['foo']", "['bar']", "['foo' 'bar']"]))
        assert c.astype(str).unique().size == 4


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


class TestExtractDateColumn(unittest.TestCase):
    """Tests the ExtractDate column_type."""

    def test_extract_date_as_string(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: event_time Random Timestamp 2021-01-01 2022-02-01
          - name: dt
            column_type: ExtractDate
            source_column: event_time
            data_type: String
            date_format: "%Y-%m-%d"

        """
        tbl = Table.parse_from_yaml(conf)

        assert len(tbl.columns) == 2
        assert isinstance(tbl.columns[1], column.ExtractDate)

        tbl.generate()

        assert tbl.df["event_time"].dtype == 'datetime64[ns]'
        assert tbl.df["dt"].dtype == 'string'

        assert all(
            tbl.df["event_time"].dt.strftime("%Y-%m-%d") == tbl.df["dt"])

    def test_extract_date_as_date(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: event_time Random Timestamp 2021-01-01 2022-02-01
          - name: dt
            column_type: ExtractDate
            data_type: Date
            source_column: event_time

        """
        tbl = Table.parse_from_yaml(conf)

        assert len(tbl.columns) == 2
        assert isinstance(tbl.columns[1], column.ExtractDate)

        tbl.generate()

        print(tbl.df.dtypes)

        assert tbl.df["event_time"].dtype == 'datetime64[ns]'
        assert tbl.df["dt"].dtype == 'object'

        assert all(tbl.df["event_time"].dt.date == tbl.df["dt"])

    def test_extract_date_as_int(self):
        conf = """
        name: mytbl
        rows: 10
        columns:
          - col: event_time Random Timestamp 2021-01-01 2022-02-01
          - name: dt
            column_type: ExtractDate
            data_type: Int
            source_column: event_time
            date_format: "%Y%m"

        """
        tbl = Table.parse_from_yaml(conf)

        assert len(tbl.columns) == 2
        assert isinstance(tbl.columns[1], column.ExtractDate)

        tbl.generate()

        #print(tbl.df)
        #print(tbl.df.dtypes)

        assert tbl.df["event_time"].dtype == 'datetime64[ns]'
        assert tbl.df["dt"].dtype == 'Int64'
