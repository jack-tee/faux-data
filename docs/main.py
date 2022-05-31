# Generate documentation
from __future__ import annotations

import inspect
import random
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
import yaml
from faux_data import column, table, target
from faux_data.factory import ColumnFactory
from jinja2 import Environment, FileSystemLoader

# set the numpy random state
np.random.seed(7)
random.seed(3)


def render_example(example: Example) -> str:

    if example.column_yaml:
        df = pd.DataFrame({"rowId": list(range(example.rows))})
        col = ColumnFactory.parse_from_yaml(example.column_yaml)
        col.maybe_add_column(df)

    elif example.columns_yaml:
        tbl = table.Table.parse_from_yaml(example.columns_yaml)
        tbl.generate()
        df = tbl.df

    else:
        raise Exception("Expected one of column_yaml or columns_yaml")

    return df.rename(columns={
        "rowId": ""
    }).to_markdown(index=False, tablefmt="github")


@dataclass
class ColumnDocs:
    columns: OrderedDict[str, ColumnDoc]

    def __post_init__(self):
        self.columns = OrderedDict(
            {c["name"]: ColumnDoc(**c)
             for c in self.columns})


@dataclass
class ColumnDoc:
    name: str
    desc: Optional[str] = None
    title: Optional[str] = None
    examples: list[str] = field(default_factory=list)
    cls = None

    def __post_init__(self):
        self.examples = [Example(**e) for e in self.examples]

        if not self.desc:
            self.desc = f"A {self.name} column"


@dataclass
class Example:
    title: str
    desc: str
    column_yaml: str | None = None
    columns_yaml: str | None = None
    rows: int = 5


def is_usable(obj):
    """
    Util function to determine if an object is usable
    i.e. it is a class but is not abstract
    """
    return inspect.isclass(obj) \
        and not inspect.isabstract(obj) \
        and issubclass(obj, (target.Target,column.Column)) \
        and not (obj is target.Target or obj is column.Column)


def main():

    env = Environment(loader=FileSystemLoader("docs/templates"))

    env.filters["render_example"] = render_example
    env.filters["cleandoc"] = inspect.cleandoc

    column_docs_dict = yaml.safe_load(open("./docs/columns.yaml"))
    column_docs = ColumnDocs(column_docs_dict["columns"])
    column_classes = inspect.getmembers(column, is_usable)

    # add the classes to the column docs
    for name, cls in column_classes:
        if name in column_docs.columns:
            (column_docs.columns[name]).cls = cls

    missing_docs = [
        c[0] for c in column_classes if c[0] not in column_docs.columns
    ]
    if missing_docs:
        print(
            f"Some column types are missing documentation and examples: {missing_docs}"
        )

    # Generate README.md
    targets = inspect.getmembers(target, is_usable)
    template = env.get_template("readme.md.jinja")
    template.stream(column_docs=column_docs, targets=targets).dump("README.md")


if __name__ == '__main__':
    main()
