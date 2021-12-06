import logging
from dataclasses import dataclass, field
from typing import List

from google.cloud import bigquery


@dataclass(kw_only=True)
class Target:
    target: str


@dataclass(kw_only=True)
class File(Target):
    filetype: str
    filepath: str

    def save(self, tbl):
        print("saved")


@dataclass(kw_only=True)
class BigQuery(Target):
    project: str
    dataset: str
    table: str
    truncate: bool = False
    post_generation_sql: str | None = None
    client = None

    def get_dataset(self, dataset_id: str):
        try:
            dataset = self.client.get_dataset(dataset_id)
        except Exception as e:
            logging.error(e)
            logging.info(f"Dataset {dataset_id} does not exist. Creating.")
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = 'europe-west2'
            dataset = self.client.create_dataset(dataset)
        return dataset

    def save(self, tbl):
        self.client = bigquery.Client()

        dataset_id = f"{self.project}.{self.dataset}"
        schema_table = f"{self.project}.{self.dataset}.{self.table}"
        dataset = self.get_dataset(dataset_id)

        job_config = None

        if self.truncate:
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)

        logging.info(f"Uploading {tbl.name} data to {schema_table}")
        result = self.client.load_table_from_dataframe(
            tbl.df, schema_table, job_config=job_config).result()

        if result.state == "DONE":
            # execute post gen sql
            pass

        logging.info(
            f"Result: {result.state} {result.output_rows} rows written to {result.destination}"
        )
