import unittest
from unittest.mock import MagicMock, ANY

import pandas as pd
from dynaconf import Dynaconf
from faux_data import target
from faux_data.factory import TargetFactory
from faux_data.table import Table
from google.cloud import bigquery

target.settings = Dynaconf(
    deployment_mode='local',
    gcp_project_id='myproject',
)

tbl_conf = {
    "name": "dummy_table",
    "rows": 10,
    "columns": [],
}
tbl = Table(**tbl_conf)

dataset = pd.DataFrame({"rowId": list(range(10))})
tbl.df = dataset


class TestLocalFileTargetParsing(unittest.TestCase):

    def test_file_target_parses(self):
        conf = """
        target: LocalFile
        filetype: csv
        filepath: path/to/my
        filename: file.csv
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.LocalFile)
        assert targ.construct_path() == "path/to/my/file.csv"
        assert targ.filetype == "csv"


class TestCloudStorageTarget(unittest.TestCase):

    def test_target_cloud_storage_target_parses(self):
        conf = """
        target: CloudStorage
        filetype: csv
        bucket: mybucket
        prefix: prefix
        filename: file.csv
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.CloudStorage)
        assert targ.construct_path() == "gs://mybucket/prefix/file.csv"
        assert targ.filetype == "csv"


class TestPubsubTarget(unittest.TestCase):

    def test_target_pubsub_target_parses(self):
        conf = """
        target: Pubsub
        topic: mytopic
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.Pubsub)
        assert targ.topic_path == "projects/myproject/topics/mytopic"

    def test_target_pubsub_target_parses_override_project(self):
        conf = """
        target: Pubsub
        topic: mytopic
        project: anotherproject
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.Pubsub)
        assert targ.topic_path == "projects/anotherproject/topics/mytopic"


class TestBigQueryTarget(unittest.TestCase):

    def test_target_bigquery_default_project(self):
        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.BigQuery)

    def test_target_bigquery_default_project_save(self):
        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.BigQuery)
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"
        mock_client.project = "myproject"

        targ.client = mock_client

        targ.save(tbl)

        expected_job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=[])

        mock_client.load_table_from_dataframe.assert_called_once_with(
            dataset, "myproject.mydataset.my_table", job_config=ANY)

        job_config = mock_client.load_table_from_dataframe.call_args.kwargs[
            "job_config"]
        assert job_config.write_disposition == expected_job_config.write_disposition
        assert job_config.schema == expected_job_config.schema

    def test_target_bigquery_specific_project_save(self):
        conf = """
        target: BigQuery
        project: anotherproject
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.BigQuery)
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"
        mock_client.project = "myproject"

        targ.client = mock_client

        targ.save(tbl)

        expected_job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=[])

        mock_client.load_table_from_dataframe.assert_called_once_with(
            dataset, "anotherproject.mydataset.my_table", job_config=ANY)

        job_config = mock_client.load_table_from_dataframe.call_args.kwargs[
            "job_config"]
        assert job_config.write_disposition == expected_job_config.write_disposition
        assert job_config.schema == expected_job_config.schema

    def test_target_bigquery_truncate_save(self):
        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        truncate: True
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.BigQuery)
        assert targ.truncate == True
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"

        targ.client = mock_client

        targ.save(tbl)

        calls = mock_client.load_table_from_dataframe.call_args
        first_call = calls[0]
        assert first_call[0] is dataset
        assert first_call[1] == "myproject.mydataset.my_table"
        self.assertEqual(calls.kwargs['job_config'].write_disposition,
                         bigquery.WriteDisposition.WRITE_TRUNCATE)

    def test_target_bigquery_no_schema_for_types(self):
        """A table with a BQ Target should not specify a schema if a Timestamp column is not present."""

        tbl_conf = """
        name: mytable
        rows: 10
        columns:
        - col: str_col Random String 3 6
        - col: int_col Random Int 3 10
        - col: float_col Random Float 3 6
        - col: dt_col Random Datetime 2022-01-01 2022-02-01 
        """

        tbl = Table.parse_from_yaml(tbl_conf)

        tbl.generate()

        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.BigQuery)
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"

        targ.client = mock_client

        targ.save(tbl)

        expected_schema = []

        mock_client.load_table_from_dataframe.assert_called_once_with(
            tbl.df, "myproject.mydataset.my_table", job_config=ANY)

        # check job config
        job_config = mock_client.load_table_from_dataframe.call_args.kwargs[
            "job_config"]
        assert job_config.schema == expected_schema

    def test_target_bigquery_schema_for_timestamp_type(self):
        """A table with a BQ Target should specify a schema if a Timestamp column is present."""

        tbl_conf = """
        name: mytable
        rows: 10
        columns:
        - col: str_col Random String 3 6
        - col: int_col Random Int 3 10
        - col: ts_col Random Timestamp 2020-01-01 2020-02-01
        - col: float_col Random Float 3 6
        - col: dt_col Random Datetime 2022-01-01 2022-02-01
        """

        tbl = Table.parse_from_yaml(tbl_conf)

        tbl.generate()

        conf = """
        target: BigQuery
        dataset: mydataset
        table: my_table
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, target.BigQuery)
        mock_client = MagicMock()
        mock_client.get_dataset.return_value = "datasetfound"

        targ.client = mock_client

        targ.save(tbl)

        expected_schema = schema = [
            bigquery.SchemaField("ts_col",
                                 bigquery.enums.SqlTypeNames.TIMESTAMP)
        ]

        mock_client.load_table_from_dataframe.assert_called_once_with(
            tbl.df, "myproject.mydataset.my_table", job_config=ANY)

        # check job config
        job_config = mock_client.load_table_from_dataframe.call_args.kwargs[
            "job_config"]
        assert job_config.schema == expected_schema
