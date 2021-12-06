import unittest

import pytest
from datafaker.table import TableParsingException
from datafaker.template import Template

from tests.utils import strip_lborder


class TestTemplateFromString(unittest.TestCase):
    def test_basic_from_string(self):
        template_str = strip_lborder("""
        tables:
          - name: mytable
            rows: 10
            targets: []
            columns:
              - col: col1 Fixed String boop
        """)
        t = Template.from_string(template_str)

        assert isinstance(t, Template)
        assert len(t.tables) == 1
        assert t.tables[0].rows == 10

    def test_basic_from_base64_string(self):
        # same template as above
        base64_str = strip_lborder("""
        dGFibGVzOgogIC0gbmFtZTogbXl0YWJsZQogICAgcm93czogMTAKICAgIHRhcmdldHM6IFtdCiAgICBjb2x1bW5zOgogICAgICAtIGNvbDogY29sMSBGaXhlZCBTdHJpbmcgYm9vcA==
        """)
        t = Template.from_base64_string(base64_str)

        assert isinstance(t, Template)
        assert len(t.tables) == 1
        assert t.tables[0].rows == 10

    def test_template_error_invalid_column(self):
        template_str = strip_lborder("""
        tables:
          - name: mytable
            rows: 10
            targets: []
            columns:
              - col: col1 Fixed String # missing value
        """)
        with pytest.raises(TableParsingException) as e:
            t = Template.from_string(template_str)

        assert "mytable" in e.__repr__()
        assert "col1" in e.__repr__()

    def test_template_error_multi_level_invalid_column(self):
        template_str = strip_lborder("""
        tables:
          - name: mytbl
            rows: 10
            columns:
              - col: message_body Map
                columns:
    
                  - col: schema Map
                    columns:
                      - col: type Fixed String struct
    
                  - col: payload Map
                    columns:
                      - col: user Map
                        columns:
                        - col: id Random # missing min, max
                        - col: email Random String 4 8
        """)
        with pytest.raises(TableParsingException) as e:
            tbl = Template.from_string(template_str)

        assert "mytbl" in e.__repr__()
        assert "message_body" in e.__repr__()
        assert "payload" in e.__repr__()
        assert "user" in e.__repr__()
        assert "id" in e.__repr__()
