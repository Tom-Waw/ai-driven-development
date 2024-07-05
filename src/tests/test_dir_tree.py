import tempfile
import unittest
from pathlib import Path

from utils import DirTreePrefix, dir_tree


class DirTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()

        path = Path(self.tmp_dir.name)
        (path / "empty_dir").mkdir()
        (path / "subdir").mkdir()

        (path / "subdir" / "file1.txt").touch()
        (path / "subdir" / "file2.txt").touch()
        (path / "file.txt").touch()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_dir_tree(self):
        path = Path(self.tmp_dir.name)
        tree = dir_tree(path)
        actual = "\n".join(tree)

        expected = "\n".join(
            [
                f"{path.name}/",
                f"{DirTreePrefix.TEE}empty_dir/",
                f"{DirTreePrefix.TEE}subdir/",
                f"{DirTreePrefix.BRANCH}{DirTreePrefix.TEE}file1.txt",
                f"{DirTreePrefix.BRANCH}{DirTreePrefix.LAST}file2.txt",
                f"{DirTreePrefix.LAST}file.txt",
            ]
        )

        self.assertEqual(actual, expected, "Directory tree did not match expected")
