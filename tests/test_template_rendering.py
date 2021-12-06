import unittest

import pytest
from datafaker.template import Template
from datafaker.template_rendering import (extract_variable_lines,
                                          render_template, resolve_variables)
from jinja2.exceptions import UndefinedError

from tests.utils import strip_lborder


class TestTemplateExtractVariableLines(unittest.TestCase):
    def test_extract_with_no_vars(self):
        template_str = strip_lborder("""
        tables:
          ...
        """)
        variables_str = extract_variable_lines(template_str)

        assert variables_str is None

    def test_extract_vars(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          dataset: {{ env }}_users
          table: {{ dataset }}.mytable

        tables:
          ...
        """)

        variable_lines = extract_variable_lines(template_str)
        print(variable_lines)

        expected = [
            "env: dev", "dataset: {{ env }}_users",
            "table: {{ dataset }}.mytable"
        ]
        assert isinstance(variable_lines, list)
        assert variable_lines == expected


class TestTemplateResolveVariables(unittest.TestCase):
    def test_resolve_nested_vars_no_runtime(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          dataset: {{ env }}_users
          table: {{ dataset }}.mytable
        tables:
          ...
        """)
        runtime_vars = {}
        builtin_vars = {}
        vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)

        expected = {
            "env": "dev",
            "dataset": "dev_users",
            "table": "dev_users.mytable"
        }
        assert expected == vars_

    def test_resolve_nested_vars_with_runtime_env(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          dataset: {{ env }}_orders
          table: {{ dataset }}.mytable
        tables:
          ...
        """)
        runtime_vars = {"env": "test"}
        builtin_vars = {}
        vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)

        expected = {
            "env": "test",
            "dataset": "test_orders",
            "table": "test_orders.mytable"
        }
        assert expected == vars_

    def test_resolve_nested_vars_with_runtime_override(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          dataset: {{ env }}_users
          table: {{ dataset }}.mytable
        tables:
          ...
        """)
        runtime_vars = {"env": "test", "dataset": "another_dataset"}
        builtin_vars = {}
        vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)

        expected = {
            "env": "test",
            "dataset": "another_dataset",
            "table": "another_dataset.mytable"
        }
        assert expected == vars_

    def test_a_builtin_var_is_overridden_by_a_runtime_var(self):
        template_str = strip_lborder("""
        tables:
          ...
        """)
        runtime_vars = {"warehouse_dir": "a/new/path"}
        builtin_vars = {"warehouse_dir": "some/path"}
        vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)

        expected = {"warehouse_dir": "a/new/path"}
        assert expected == vars_

    def test_a_template_var_is_overridden_by_a_runtime_var(self):
        template_str = strip_lborder("""
        variables:
          type: banana 
        tables:
          ...
        """)
        runtime_vars = {"type": "apple"}
        builtin_vars = {}
        vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)

        expected = {"type": "apple"}
        assert expected == vars_


class TestTemplateRenderTemplate(unittest.TestCase):
    def test_basic_render(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          fileext: csv
        
        tables:
          - name: mytable
            targets: 
              target: file
              filepath: data/{{ env }}/myfile.{{ fileext }}
            columns:
              ... 
        """)
        runtime_vars = {}
        builtin_vars = {}

        rendered_template = render_template(template_str, runtime_vars)

        assert "filepath: data/dev/myfile.csv" in rendered_template

    def test_basic_override_render(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          fileext: csv
        
        tables:
          - name: mytable
            targets: 
              target: file
              filepath: data/{{ env }}/myfile.{{ fileext }}
            columns:
              ... 
        """)
        runtime_vars = {"env": "prod"}

        rendered_template = render_template(template_str, runtime_vars)

        assert "filepath: data/prod/myfile.csv" in rendered_template

    def test_basic_ts_render(self):
        template_str = strip_lborder("""
        variables:
          env: dev
          filename: path/to/{{ env }}/file_{{ start.strftime("%Y_%m") }}.csv
        
        tables:
          - name: mytable
            targets: 
              target: file
              filepath: {{ filename }}
            columns:
              ... 
        """)
        runtime_vars = {"env": "prod", "start": "2021-03-04"}

        rendered_template = render_template(template_str, runtime_vars)

        assert "filepath: path/to/prod/file_2021_03.csv" in rendered_template

    def test_missing_var_render(self):
        template_str = strip_lborder("""
        variables:
          env: dev
        
        tables:
          - name: mytable
            targets: 
              target: file
              filepath: data/{{ env }}/myfile.{{ fileext }}
            columns:
              ... 
        """)
        runtime_vars = {"env": "prod"}

        with pytest.raises(UndefinedError) as e:
            _ = render_template(template_str, runtime_vars)

        assert "fileext" in e.__repr__()
