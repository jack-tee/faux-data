# Generate documentation
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import inspect

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader
from faux_data.factory import ColumnFactory
from faux_data import target, column


def render_column_example(example: Example) -> str:
    df = pd.DataFrame({"rowId": list(range(example.rows))})
    col = ColumnFactory.parse_from_yaml(example.yaml)
    col.maybe_add_column(df)

    return df.rename(columns={
        "rowId": ""
    }).to_markdown(index=False, tablefmt="github")


@dataclass
class ColumnDocs:
    columns: list[ColumnDoc]

    def __post_init__(self):
        self.columns = [ColumnDoc(**c) for c in self.columns]


@dataclass
class ColumnDoc:
    name: str
    desc: Optional[str] = None
    title: Optional[str] = None
    examples: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.examples = [Example(**e) for e in self.examples]

        if not self.desc:
            self.desc = f"A {self.name} column"


@dataclass
class Example:
    desc: str
    yaml: str
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

    env.filters["render_column_example"] = render_column_example
    env.filters["cleandoc"] = inspect.cleandoc

    # Generate COLUMNS.md
    column_docs = yaml.safe_load(open("./docs/column_docs.yaml"))
    column_docs = ColumnDocs(column_docs["columns"])
    template = env.get_template("column_docs.jinja")
    template.stream(columns=column_docs).dump("COLUMNS.md")

    # Generate README.md
    targets = inspect.getmembers(target, is_usable)
    columns = inspect.getmembers(column, is_usable)
    template = env.get_template("readme.md.jinja")
    template.stream(columns=columns, targets=targets).dump("README.md")


if __name__ == '__main__':
    main()
