import unittest
from unittest.mock import MagicMock

import pandas as pd
from datafaker.factory import TargetFactory
from datafaker.table import Table
from datafaker.target import BigQuery, File
from google.cloud import bigquery

tbl_conf = {
    "name": "dummy_table",
    "rows": 10,
    "columns": [],
}
tbl = Table(**tbl_conf)

dataset = pd.DataFrame({"rowId": list(range(10))})
tbl.df = dataset


class TestTargetParsing(unittest.TestCase):
    # Fixed Column
    def test_file_target_parses(self):
        conf = """
        target: File
        filetype: csv
        filepath: path/to/my/file.csv
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, File)
        assert targ.filepath == "path/to/my/file.csv"
        assert targ.filetype == "csv"


class TestBigQueryTarget(unittest.TestCase):
    def test_target_bigquery_default_project(self):
        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, BigQuery)

    def test_target_bigquery_default_project_save(self):
        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, BigQuery)
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"
        mock_client.project = "myproject"

        targ.client = mock_client

        targ.save(tbl)

        mock_client.load_table_from_dataframe.assert_called_once_with(
            dataset, "myproject.mydataset.my_table", job_config=None)

    def test_target_bigquery_specific_project_save(self):
        conf = """
        target: BigQuery
        project: anotherproject
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, BigQuery)
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"
        mock_client.project = "myproject"

        targ.client = mock_client

        targ.save(tbl)

        mock_client.load_table_from_dataframe.assert_called_once_with(
            dataset, "anotherproject.mydataset.my_table", job_config=None)

    def test_target_bigquery_truncate_save(self):
        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        truncate: True
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, BigQuery)
        assert targ.truncate == True
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"
        mock_client.project = "myproject"

        targ.client = mock_client

        targ.save(tbl)

        calls = mock_client.load_table_from_dataframe.call_args
        first_call = calls[0]
        assert first_call[0] is dataset
        assert first_call[1] == "myproject.mydataset.my_table"
        self.assertEqual(calls.kwargs['job_config'].write_disposition,
                         bigquery.WriteDisposition.WRITE_TRUNCATE)
