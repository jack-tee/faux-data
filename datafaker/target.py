import logging
import os
from dataclasses import dataclass, field
from typing import Optional, Tuple
import time

import pandas as pd

from .config import GOOGLE_PROJECT_ID


@dataclass(kw_only=True)
class Target:
    """Base class for all targets."""

    target: str


@dataclass(kw_only=True)
class PartitionedFileTarget(Target):
    """Base class for targets that create partitioned files."""

    filetype: str
    partition_cols: list[str] = field(default_factory=list)

    def construct_path(self, partition_path=None) -> str:
        pass

    def pre_save_object(self, path):
        pass

    def save(self, tbl):
        if self.partition_cols:
            partitions = tbl.df.groupby(self.partition_cols)
            for partition in partitions:
                if len(self.partition_cols) == 1:
                    partition_path = f"{self.partition_cols[0]}={partition[0]}"
                else:
                    partition_path = '/'.join((f"{p}={v}" for p,v in zip(self.partition_cols, partition[0])))
                path = self.construct_path(partition_path)

                df = partition[1].drop(self.partition_cols, axis=1)
                self.save_object(df, path)

        else:
            path = self.construct_path()
            self.save_object(tbl.df, path)

    def save_object(self, df, path):

        self.pre_save_object(path)

        logging.debug(f"saving data to {path}")
        match self.filetype:
            case 'csv':
                df.to_csv(path, index=False)
            case 'parquet':
                df.to_parquet(path, index=False)
            case _:
                raise Exception(f"unrecognised filetype: [{self.filetype}]")


@dataclass(kw_only=True)
class CloudStorage(PartitionedFileTarget, Target):
    bucket: str
    prefix: str
    filename: str

    def construct_path(self, partition_path=None) -> str:
        if partition_path:
            return f"gs://{self.bucket}/{self.prefix}/{partition_path}/{self.filename}"
        else:
            return f"gs://{self.bucket}/{self.prefix}/{self.filename}"


@dataclass(kw_only=True)
class LocalFile(PartitionedFileTarget, Target):
    """Target for creating files on the local file system."""

    filepath: str
    filename: str

    def construct_path(self, partition_path=None) -> str:
        if partition_path:
            return f"{self.filepath}/{partition_path}/{self.filename}"
        else:
            return f"{self.filepath}/{self.filename}"
    
    def pre_save_object(self, path):

        if not os.path.exists(os.path.dirname(path)):
            logging.debug(f"creating dir {os.path.dirname(path)}")
            os.makedirs(os.path.dirname(path), exist_ok=True)


    


@dataclass(kw_only=True)
class BigQuery(Target):
    """Target for loading data to BigQuery."""

    project: str | None = None
    dataset: str
    table: str
    truncate: bool = False
    post_generation_sql: str | None = None
    client = None
    bigquery = None

    def setup(self):
        from google.cloud import bigquery
        self.bigquery = bigquery

        if not self.client:
            self.client = bigquery.Client()
        
        if not self.project:
            self.project = GOOGLE_PROJECT_ID
            

    def get_or_create_dataset(self, dataset_id: str):
        try:
            dataset = self.client.get_dataset(dataset_id)
        except Exception as e:
            logging.error(e)
            logging.info(f"Dataset {dataset_id} does not exist. Creating.")
            dataset = self.bigquery.Dataset(dataset_id)
            dataset.location = 'europe-west2'
            dataset = self.client.create_dataset(dataset)
        return dataset

    def save(self, tbl):
        self.setup()

        dataset_id = f"{self.project}.{self.dataset}"
        schema_table = f"{self.project}.{self.dataset}.{self.table}"
        dataset = self.get_or_create_dataset(dataset_id)

        job_config = None

        if self.truncate:
            job_config = self.bigquery.LoadJobConfig(
                write_disposition=self.bigquery.WriteDisposition.WRITE_TRUNCATE)

        logging.info(f"Uploading {tbl.name} data to {schema_table}")
        result = self.client.load_table_from_dataframe(
            tbl.df, schema_table, job_config=job_config).result()

        if self.post_generation_sql and result.state == "DONE":
            self.client.query(self.post_generation_sql.format(t=self),
                              project=self.project).result()

        logging.info(
            f"Result: {result.state} {result.output_rows} rows written to {result.destination}"
        )


@dataclass(kw_only=True)
class StreamingTarget(Target):
    """Base class for targets that send data to streaming systems."""

    def process_row(self, row):
        pass

    def setup(self):
        pass

    def save(self, tbl):
        self.setup()

        for row in tbl.df.iterrows():
            self.process_row(row)



@dataclass(kw_only=True)
class Pubsub(StreamingTarget, Target):
    """Target for sending data to Pubsub."""

    topic: str
    project: Optional[str] = None

    output_cols: list[str] = field(default_factory=list)
    attribute_cols: list[str] = field(default_factory=list)
    attributes: dict[str,str] = field(default_factory=dict)
    
    delay: float = 0.01
    date_format: str = 'iso' # or epoch
    time_unit: str = 'ms'
    validate_first: bool = True
    client = None

    def __post_init__(self):
        if not self.project:
            self.project = GOOGLE_PROJECT_ID

    @property
    def topic_path(self):
        return f"projects/{self.project}/topics/{self.topic}"

    def setup(self):
        from google.cloud import pubsub_v1

        if not self.client:
            self.client = pubsub_v1.PublisherClient()

    def process_row(self, row, row_attrs):
        return self.client.publish(self.topic_path, row.encode(), **row_attrs, **self.attributes)

    def process_df(self, df) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        if self.attribute_cols:
            attributes_df = df[self.attribute_cols].astype('string')
        else:
            attributes_df = None
        
        if self.output_cols:
            data_df = df[self.output_cols]
        else:
            data_df = df.drop(self.attribute_cols, axis=1)

        return data_df, attributes_df
            


    def save(self, tbl):
        self.setup()

        data_df, attributes_df = self.process_df(tbl.df)

        json_data = data_df.to_json(
            orient='records',
            lines=True,
            date_format=self.date_format,
            date_unit=self.time_unit).strip().split("\n")

        for i, row in enumerate(json_data):
            
            if attributes_df is not None:
                row_attrs = attributes_df.iloc[i].to_dict()
            else:
                row_attrs = None

            if self.validate_first:
                res = self.process_row(row, row_attrs)
                logging.info(f"publishing first message to topic [{self.topic_path}] with data: [{row}] and attributes: [{row_attrs}] message_id: {res.result()}")
                self.validate_first = False
            else:
                res = self.process_row(row, row_attrs)
            
            if self.delay > 0:
                time.sleep(self.delay)
