import unittest
from unittest.mock import MagicMock

from datafaker.factory import TargetFactory
from datafaker.target import File, BigQuery


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

        targ.save()

        assert mock_client.load_table_from_dataframe.assert_called_once_with()
