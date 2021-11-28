import pytest
import unittest

from datafaker.table import Table


class TestTableParsing(unittest.TestCase):
    def test_basic_table_parsing_error_on_column(self):
        conf = """
        name: mytable
        rows: 10
        columns:
        - name: mycol
          column_type: Fixed
          # value: missing 
        """
        tbl = Table.parse_from_yaml(conf)

        assert tbl.complete == False
        msg = tbl.error.__repr__()
        assert "mycol" in msg
        assert "'value'" in msg


class TestTableGeneration(unittest.TestCase):
    def test_basic_single_column_table_parses(self):
        conf = """
        name: mytable
        rows: 10
        columns:
        - name: mycol
          column_type: Fixed
          value: b
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        print("\n")
        print(tbl.df.to_string(index=False))

        assert len(tbl.df.columns) == 1
        assert len(tbl.df) == 10

    def test_basic_multi_column_table_parses(self):
        conf = """
        name: mytable
        rows: 11
        columns:
        - name: col1
          column_type: Fixed
          value: b
        - name: col2
          column_type: Random
          min: 3
          max: 10
        """
        tbl = Table.parse_from_yaml(conf)
        tbl.generate()

        print("\n")
        print(tbl.df.to_string(index=False))

        assert len(tbl.df.columns) == 2
        assert len(tbl.df) == 11
