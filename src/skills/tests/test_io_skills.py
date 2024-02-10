import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from skills.io_skills import FileAction, FileChange, delete_file_or_dir, modify_file, overwrite_file, read_file

EXISTING_FILE_PATH = "existing_file.txt"
MULTILINE_FILE_PATH = "multiline_file.txt"


class IOSkillsTests(unittest.TestCase):
    def setUp(self):
        # Reset the test environment before each test
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch("settings.Settings.WORK_DIR", self.temp_dir)
        self.patcher.start()

        # ? Existing File
        with open(os.path.join(self.temp_dir, EXISTING_FILE_PATH), "w") as f:
            f.write("Initial content")

        # ? Multi Line File
        with open(os.path.join(self.temp_dir, MULTILINE_FILE_PATH), "w") as f:
            f.writelines(["Line 1\n", "Line 2\n", "Line 3\n"])

        # ? Symbolic Link:
        symlink_target = os.path.join(self.temp_dir, EXISTING_FILE_PATH)
        symlink_path = os.path.join(self.temp_dir, "link_to_existing")
        os.symlink(symlink_target, symlink_path)

        # ? Subdirectory
        os.mkdir(os.path.join(self.temp_dir, "subdir"))

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.temp_dir)

    # ? Test cases for the read_file function

    def test_read_existing_file(self):
        content = read_file(EXISTING_FILE_PATH)
        self.assertEqual(content, "Initial content", "File content did not match expected")

    def test_read_non_existing_file(self):
        with self.assertRaises(ValueError):
            read_file("non_existing_file.txt")

    def test_read_file_symlink(self):
        with self.assertRaises(ValueError):
            read_file("link_to_existing")

    def test_path_traversal_attempt(self):
        # Attempt to access a file outside the temp directory
        with self.assertRaises(ValueError):
            read_file("../../outside.txt")

    # ? Test cases for the overwrite_file function

    def test_overwrite_file(self):
        new_content = "New content"
        overwrite_file(EXISTING_FILE_PATH, new_content)

        with open(os.path.join(self.temp_dir, EXISTING_FILE_PATH), "r") as f:
            content = f.read()

        self.assertEqual(content, new_content, "File should have been overwritten with new content")

    def test_create_file_in_non_existing_path(self):
        overwrite_file("subdir/subsubdir/new_file.txt", "New content")

        with open(os.path.join(self.temp_dir, "subdir/subsubdir/new_file.txt"), "r") as f:
            content = f.read()

        self.assertEqual(content, "New content", "File should have been created in the non-existing path")

    # ? Test cases for the modify_file function

    def test_modify_file_complex_changes(self):
        changes = [
            FileChange(action=FileAction.WRITE, line_number=1, content="Altered Line 1"),
            FileChange(action=FileAction.REMOVE, line_number=2, content="Useless Content"),
            FileChange(action=FileAction.WRITE, line_number=4, content="New Line at End"),
        ]
        modify_file(MULTILINE_FILE_PATH, changes)

        expected_content = ["Altered Line 1\n", "Line 3\n", "New Line at End\n"]
        # Verify the file content
        with open(os.path.join(self.temp_dir, MULTILINE_FILE_PATH), "r") as f:
            content = f.readlines()

        self.assertEqual(content, expected_content, "File content did not match expected changes")

    def test_modify_file_invalid_path(self):
        with self.assertRaises(ValueError):
            modify_file("non_existing_file.txt", [])

    def test_modify_file_invalid_line_number(self):
        with self.assertRaises(ValueError):
            modify_file(EXISTING_FILE_PATH, [FileChange(action=FileAction.WRITE, line_number=-1, content="Invalid")])

    # ? Test cases for the delete_file_or_dir function

    def test_delete_existing_file(self):
        delete_file_or_dir(EXISTING_FILE_PATH)
        self.assertFalse(os.path.exists(EXISTING_FILE_PATH), "File should have been deleted")

    def test_delete_dir(self):
        delete_file_or_dir("subdir")
        self.assertFalse(os.path.exists("subdir"), "Directory should have been deleted")
