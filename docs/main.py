# Generate documentation
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader
from datafaker.factory import ColumnFactory


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


def main():

    env = Environment(loader=FileSystemLoader("docs/templates"))

    env.filters["render_column_example"] = render_column_example

    # Generate COLUMNS.md
    column_docs = yaml.safe_load(open("./docs/column_docs.yaml"))
    column_docs = ColumnDocs(column_docs["columns"])
    template = env.get_template("column_docs.jinja")
    template.stream(columns=column_docs).dump("COLUMNS.md")


if __name__ == '__main__':
    main()
