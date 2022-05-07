import unittest

import pytest
from datafaker.cmd import parse_params

simple_tests = [
    ("--start 2021-03-02", {
        "start": "2021-03-02"
    }),
    ("--other blah", {
        "other": "blah"
    }),
    ("--one one --two two", {
        "one": "one",
        "two": "two"
    }),
    ("--withquotes '2021-04-03 00:03:02' --other 'bloop'", {
        "withquotes": "2021-04-03 00:03:02",
        "other": "bloop"
    }),
    ("--equals=yope --other 'bloop'", {
        "equals": "yope",
        "other": "bloop"
    }),
    ("--debug", {
        "debug": True,
    }),
    ("--debug --foo=bar", {
        "debug": True,
        "foo": "bar",
    }),
    ("--debug --foo bar", {
        "debug": True,
        "foo": "bar",
    }),
    ("--debug --foo bar --last", {
        "debug": True,
        "foo": "bar",
        "last": True,
    }),
    ("--debug --foo bar --last --finally", {
        "debug": True,
        "foo": "bar",
        "last": True,
        "finally": True,
    }),
    ("--debug --foo bar --last --finally=boop", {
        "debug": True,
        "foo": "bar",
        "last": True,
        "finally": "boop",
    }),
]


@pytest.mark.parametrize("cli_str,expected_params", simple_tests)
def test_cmd_parse_basic(cli_str, expected_params):

    cli_args = cli_str.split()
    params = parse_params(cli_args)

    assert expected_params == params
