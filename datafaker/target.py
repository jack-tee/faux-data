from dataclasses import dataclass, field
from typing import List


@dataclass(kw_only=True)
class Target:
    type: str


@dataclass(kw_only=True)
class File(Target):
    pass