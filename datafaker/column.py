import dataclasses
from dataclasses import dataclass, field
from typing import List
import importlib

import numpy as np
import pandas as pd
import yaml

from datafaker.utils import get_parts

pandas_type_mapping = {"Int": "int64", "String": "string", "Float": "float64"}


@dataclass(kw_only=True)
class Column:
    name: str
    column_type: str
    data_type: str = None

    @classmethod
    def get_subclass(cls, key: str):
        importlib.import_module("datafaker.columns")
        for c in cls.__subclasses__():
            if c.__name__ == key:
                return c
        raise NotImplementedError("Could not find class named in subclasses")

    @classmethod
    def parse_from_yaml(cls, yaml_str):
        conf = yaml.safe_load(yaml_str)
        return cls.parse(conf)

    @classmethod
    def parse(cls, conf: dict):
        """Read the column configuration and return the specified column type."""

        if conf.get("col"):
            column_type = conf.get("col").split()[1]

        elif conf.get("column_type"):
            column_type = conf.get("column_type")

        else:
            raise NotImplementedError("Could not determine column_type")

        c = cls.get_subclass(column_type)

        return c.build(conf)

    @classmethod
    def build(cls, conf: dict):
        """Build the column type from the provided column configuration."""

        if conf.get("column_type"):
            return cls(**conf)

        elif conf.get("col"):
            parts = get_parts(conf.get("col"))
            for f, conf_part in zip(dataclasses.fields(cls), parts):

                if f.type == List[any]:
                    # skip any iterable fields
                    continue
                elif f.type != any:
                    conf[f.name] = f.type(conf_part.strip())
                else:
                    conf[f.name] = conf_part.strip()

            del conf["col"]

            return cls(**conf)

    def maybe_add_column(self, df: pd.DataFrame) -> None:
        try:
            self.add_column(df)
        except Exception as e:
            raise ColumnGenerationException(
                f"Error on column [{self.name}]. Caused by: {e}.")

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = self.generate(len(df))

    def generate(self, rows: int) -> pd.Series:
        raise NotImplementedError("Please Implement this method")

    def pandas_type(self) -> str:
        if self.data_type:
            return pandas_type_mapping.get(self.data_type)
        return None


class ColumnGenerationException(Exception):
    pass