import unittest

from datafaker.factory import TargetFactory
from datafaker.target import File


class TestTargetParsing(unittest.TestCase):
    # Fixed Column
    def test_file_target_parses(self):
        conf = """
        target: File
        filetype: csv
        filepath: path/to/my/file.csv
        """
        targ = TargetFactory.parse_from_yaml(conf)
        assert isinstance(targ, File)
        assert targ.filepath == "path/to/my/file.csv"
        assert targ.filetype == "csv"