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
]


@pytest.mark.parametrize("cli_str,expected_params", simple_tests)
def test_cmd_parse_basic(cli_str, expected_params):

    cli_args = cli_str.split()
    params = parse_params(cli_args)

    assert expected_params == params
