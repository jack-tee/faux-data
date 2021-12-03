from dataclasses import dataclass, field
from typing import List

import yaml

from .table import Table


@dataclass(kw_only=True)
class Template:
    variables: dict = field(default_factory=dict, repr=False)
    tables: List[Table]

    def __init__(self, tables: dict, variables: dict = None):
        self.tables = [Table(**table) for table in tables]

    def generate(self):
        for table in self.tables:
            table.generate()

    def result(self):
        return '/n'.join(t.result() for t in self.tables)

    @classmethod
    def from_string(cls, template_str):
        parsed = yaml.safe_load(template_str)
        return cls(**parsed)

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, "r") as f:
            template_str = f.read()
        return cls.from_string(template_str)

    @classmethod
    def resolve_variables(cls, template_str):

        return template_str
