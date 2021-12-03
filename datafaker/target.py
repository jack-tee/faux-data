from dataclasses import dataclass, field
from typing import List


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

    def save(self, tbl):
        print("saved")