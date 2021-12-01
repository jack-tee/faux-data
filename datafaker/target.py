from dataclasses import dataclass, field
from typing import List

from .template_entity import TemplateEntity


@dataclass(kw_only=True)
class Target(TemplateEntity):
    type_key: str = field(default="target", init=False)
    short_key: str = field(default="t", init=False)
    short_skip_fields: str = field(default="", init=False)
    import_path: str | None = field(default="", init=False)

    target: str


@dataclass(kw_only=True)
class File(Target):
    filetype: str
    filepath: str

    def save(self, tbl):
        print("saved")
