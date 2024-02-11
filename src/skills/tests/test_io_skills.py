import os
import shutil
import tempfile
import unittest
from ast import Delete
from unittest.mock import patch

from settings import Settings
from skills.base import Skill
from skills.io_skills import (
    CodingSkillSet,
    DeleteFileOrDirSkill,
    FileAction,
    FileChange,
    ModifyFileSkill,
    OverwriteFileSkill,
    ReadFileSkill,
)

EXISTING_FILE_PATH = "existing_file.txt"
MULTILINE_FILE_PATH = "multiline_file.txt"


class IOSkillsTests(unittest.TestCase):
    def setUp(self):
        # Reset the test environment before each test
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch.object(Settings, "WORK_DIR", self.temp_dir)
        self.patcher.start()

        self.skill_set = CodingSkillSet(Settings.WORK_DIR)

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

    def get_skill(self, skill_cls: type[Skill]) -> Skill:
        return next(skill for skill in self.skill_set.skills if isinstance(skill, skill_cls))

    # ? Test cases for the read_file function

    def test_read_existing_file(self):
        skill = self.get_skill(ReadFileSkill)
        content = skill.execute(EXISTING_FILE_PATH)

        self.assertEqual(content, "Initial content", "File content did not match expected")

    def test_read_non_existing_file(self):
        skill = self.get_skill(ReadFileSkill)

        with self.assertRaises(ValueError):
            skill.execute("non_existing_file.txt")

    def test_read_file_symlink(self):
        skill = self.get_skill(ReadFileSkill)

        with self.assertRaises(ValueError):
            skill.execute("link_to_existing")

    def test_path_traversal_attempt(self):
        skill = self.get_skill(ReadFileSkill)

        with self.assertRaises(ValueError):
            # Attempt to access a file outside the temp directory
            skill.execute("../../outside.txt")

    # ? Test cases for the overwrite_file function

    def test_overwrite_file(self):
        skill = self.get_skill(OverwriteFileSkill)

        new_content = "New content"
        skill.execute(EXISTING_FILE_PATH, new_content)

        with open(os.path.join(self.temp_dir, EXISTING_FILE_PATH), "r") as f:
            content = f.read()

        self.assertEqual(content, new_content, "File should have been overwritten with new content")

    def test_create_file_in_non_existing_path(self):
        skill = self.get_skill(OverwriteFileSkill)

        skill.execute("subdir/subsubdir/new_file.txt", "New content")

        with open(os.path.join(self.temp_dir, "subdir/subsubdir/new_file.txt"), "r") as f:
            content = f.read()

        self.assertEqual(content, "New content", "File should have been created in the non-existing path")

    # ? Test cases for the modify_file function

    def test_modify_file_complex_changes(self):
        skill = self.get_skill(ModifyFileSkill)

        changes = [
            FileChange(action=FileAction.WRITE, line_number=1, content="Altered Line 1"),
            FileChange(action=FileAction.REMOVE, line_number=2, content="Useless Content"),
            FileChange(action=FileAction.WRITE, line_number=4, content="New Line at End"),
        ]
        skill.execute(MULTILINE_FILE_PATH, changes)

        expected_content = ["Altered Line 1\n", "Line 3\n", "New Line at End\n"]
        # Verify the file content
        with open(os.path.join(self.temp_dir, MULTILINE_FILE_PATH), "r") as f:
            content = f.readlines()

        self.assertEqual(content, expected_content, "File content did not match expected changes")

    def test_modify_file_invalid_path(self):
        skill = self.get_skill(ModifyFileSkill)

        with self.assertRaises(ValueError):
            skill.execute("non_existing_file.txt", [])

    def test_modify_file_invalid_line_number(self):
        skill = self.get_skill(ModifyFileSkill)

        with self.assertRaises(ValueError):
            skill.execute(EXISTING_FILE_PATH, [FileChange(action=FileAction.WRITE, line_number=-1, content="Invalid")])

    # ? Test cases for the delete_file_or_dir function

    def test_delete_existing_file(self):
        skill = self.get_skill(DeleteFileOrDirSkill)
        skill.execute(EXISTING_FILE_PATH)

        self.assertFalse(os.path.exists(EXISTING_FILE_PATH), "File should have been deleted")

    def test_delete_dir(self):
        skill = self.get_skill(DeleteFileOrDirSkill)
        skill.execute("subdir")

        self.assertFalse(os.path.exists("subdir"), "Directory should have been deleted")
