import dataclasses
from dataclasses import dataclass, field
import importlib
import re
from typing import List

import yaml


@dataclass(kw_only=True)
class TemplateEntity:
    """Base class for Columns and Targets"""
    type_key: str = field(metadata={"base": True})
    short_key: str
    short_skip_fields: str
    import_path: str | None = None

    @classmethod
    def get_subclass(cls, key: str):
        if cls.import_path:
            importlib.import_module(cls.import_path)
        for c in cls.__subclasses__():
            if c.__name__ == key:
                return c
        raise NotImplementedError(
            f"Could not find class named [{key}] in subclasses")

    @classmethod
    def parse_from_yaml(cls, yaml_str):
        conf = yaml.safe_load(yaml_str)
        return cls.parse(conf)

    @classmethod
    def parse(cls, conf: dict):
        """Read the column configuration and return the specified column type."""

        if conf.get(cls.short_key):
            type_ = conf.get(cls.short_key).split()[1]

        elif conf.get(cls.type_key):
            type_ = conf.get(cls.type_key)

        else:
            raise NotImplementedError(
                f"Could not determine type. Missing key {cls.type_key}")

        c = cls.get_subclass(type_)

        return c.build(conf)

    @classmethod
    def build(cls, conf: dict):
        """Build the column type from the provided column configuration."""

        if conf.get(cls.type_key):
            return cls(**conf)

        elif conf.get(cls.short_key):
            parts = get_parts(conf.get(cls.short_key))
            fields = [
                f for f in dataclasses.fields(cls)
                if f.name not in cls.short_skip_fields.split(",")
                and f.type != List[any] and f.init == True
            ]
            for f, conf_part in zip(fields, parts):
                if f.type != any:
                    conf[f.name] = f.type(conf_part.strip())
                else:
                    conf[f.name] = conf_part.strip()

            del conf[cls.short_key]

            return cls(**conf)


def get_parts(val: str):
    """Splits a string into parts respecting double and single quotes
    
    Examples:
        >>> get_parts("mycol Random Timestamp \"2023-03-03 00:00:00\" '2026-12-12 23:59:59'")
        ["mycol", "Random", "Timestamp", "2023-03-03 00:00:00", "2026-12-12 23:59:59"]

    """
    groups = re.findall(r"[ ]?(?:(?!\"|')(\S+)|(?:\"|')(.+?)(?:\"|'))[ ]?",
                        val)

    # there are two matching groups for the two cases so get the first non empty val
    def first_non_empty(g):
        if g[0]:
            return g[0]
        else:
            return g[1]

    return [first_non_empty(group) for group in groups]