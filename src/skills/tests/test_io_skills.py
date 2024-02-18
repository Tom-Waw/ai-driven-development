import inspect
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Annotated, Type, TypeVar
from unittest.mock import patch

from settings import Settings
from skills.base import Skill
from skills.io_skills import (
    CodingSkillSet,
    CreateOrOverwriteFileSkill,
    DeleteFileOrDirSkill,
    DirTreePrefix,
    DirTreeSkill,
    FileAction,
    FileChange,
    ListDirSkill,
    ModifyFileSkill,
    ReadFileSkill,
    SafePathSkill,
)

EXISTING_FILE_PATH = "existing_file.txt"
MULTILINE_FILE_PATH = "multiline_file.txt"


SkillTypeVar = TypeVar("SkillTypeVar", bound=Skill)


class IOSkillsTests(unittest.TestCase):
    def setUp(self):
        # Reset the test environment before each test
        self.temp_dir = Path(tempfile.mkdtemp())
        self.patcher = patch.object(Settings, "WORK_DIR", self.temp_dir)
        self.patcher.start()

        self.skill_set = CodingSkillSet(Settings.WORK_DIR)

        # ? Existing File
        with open(self.temp_dir / EXISTING_FILE_PATH, "w") as f:
            f.write("Initial content")

        # ? Multi Line File
        with open(self.temp_dir / MULTILINE_FILE_PATH, "w") as f:
            f.writelines(["Line 1\n", "Line 2\n", "Line 3\n"])

        # ? Symbolic Link:
        symlink_target = self.temp_dir / EXISTING_FILE_PATH
        symlink_path = self.temp_dir / "link_to_existing"
        os.symlink(symlink_target, symlink_path)

        # ? Subdirectory
        nested_sub_dir = self.temp_dir / "subdir" / "nested_subdir"
        nested_sub_dir.mkdir(parents=True, exist_ok=True)

        # ? Nested File:
        with open(nested_sub_dir / "nested_file.txt", "w") as f:
            f.write("Nested file content")

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.temp_dir)

    def get_skill(self, skill_cls: Type[SkillTypeVar]) -> SkillTypeVar:
        return next(skill for skill in self.skill_set.skills if isinstance(skill, skill_cls))

    # ? Test cases for execute signature of the skills

    def test_execute_signature(self):
        description = "Path to manipulate"
        description2 = "Some extra data"

        class TestSkill(SafePathSkill):

            def safe_execute(
                self,
                extra: Annotated[int, description2],
                path: Annotated[Path, description] = Path(""),
            ) -> Path:
                return path

        skill = TestSkill(work_dir=Settings.WORK_DIR)
        result = skill.execute(extra=42, path="test")

        # Check converted path
        self.assertEqual(result, Settings.WORK_DIR / "test", "Skill did not execute as expected")

        # Check signature of the execute method
        expected_signature = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    "extra",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[int, description2],
                ),
                inspect.Parameter(
                    "path",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=".",
                    annotation=Annotated[Path, description],
                ),
            ],
            return_annotation=Path,
        )
        self.assertEqual(
            inspect.signature(skill.execute),
            expected_signature,
            "Signature of the execute method did not match expected",
        )

    # ? Test cases for the list_dir function

    def test_list_dir(self):
        skill = self.get_skill(ListDirSkill)
        dir_content = skill.execute()

        self.assertEqual(
            dir_content,
            ["link_to_existing", EXISTING_FILE_PATH, "subdir", MULTILINE_FILE_PATH],
            "Directory content did not match expected",
        )

    # ? Test cases for the dir_tree function

    def test_dir_tree(self):
        skill = self.get_skill(DirTreeSkill)
        tree = skill.execute()

        expected_tree = "\n".join(
            [
                f"{DirTreePrefix.TEE}link_to_existing",
                f"{DirTreePrefix.TEE}{EXISTING_FILE_PATH}",
                f"{DirTreePrefix.TEE}subdir",
                f"{DirTreePrefix.BRANCH}{DirTreePrefix.LAST}nested_subdir",
                f"{DirTreePrefix.BRANCH}{DirTreePrefix.SPACE}{DirTreePrefix.LAST}nested_file.txt",
                f"{DirTreePrefix.LAST}{MULTILINE_FILE_PATH}",
            ]
        )

        self.assertEqual(tree, expected_tree, "Directory tree did not match expected")

    # ? Test cases for the read_file function

    def test_read_existing_file(self):
        skill = self.get_skill(ReadFileSkill)
        content = skill.execute(EXISTING_FILE_PATH)

        self.assertEqual(content, "1: Initial content", "File content did not match expected")

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
        skill = self.get_skill(CreateOrOverwriteFileSkill)

        new_content = "New content"
        skill.execute(EXISTING_FILE_PATH, new_content)

        with open(os.path.join(self.temp_dir, EXISTING_FILE_PATH), "r") as f:
            content = f.read()

        self.assertEqual(content, new_content, "File should have been overwritten with new content")

    def test_create_file_in_non_existing_path(self):
        skill = self.get_skill(CreateOrOverwriteFileSkill)

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
