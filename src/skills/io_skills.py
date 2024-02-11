import os
import stat
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Annotated, Callable

from typing_extensions import Self

from settings import Settings
from skills.base import Skill, SkillSet


class SafePathSkill(Skill, ABC):
    raise_on_404 = False

    def __init__(self, work_dir: str = Settings.CODE_DIR, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.work_dir = work_dir

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Automatically wrap the execute method of subclasses with path validation
        original_execute = cls.execute

        @wraps(original_execute)
        def safe_execute(self, path: str, *args, **kwargs):
            safe_path = self._validate_and_resolve_path(path)
            return original_execute(self, *args, path=safe_path, **kwargs)

        cls.execute = safe_execute

    def _validate_and_resolve_path(self, path: str) -> str:
        safe_path = os.path.abspath(os.path.join(self.work_dir, path))

        if self.raise_on_404 and not os.path.exists(safe_path):
            raise ValueError("File does not exist at path: " + path)

        if not os.path.commonpath([safe_path, self.work_dir]) == self.work_dir:
            raise ValueError("Access denied: Attempted access outside of working directory at path: " + path)

        if os.path.islink(safe_path):
            raise ValueError("Security alert: Path is a symbolic link at path: " + path)

        return safe_path


class ListDirSkill(SafePathSkill):
    description = "List the content of a directory."
    raise_on_404 = True

    def execute(self, path: Annotated[str, "Path of directory to list"]) -> list[str]:
        """List the content of a directory"""
        return os.listdir(path)


class ReadFileSkill(SafePathSkill):
    description = "Read the content of a file."
    raise_on_404 = True

    def execute(self, path: Annotated[str, "Path of file to read"]) -> str:
        """Read the content of a file"""
        with open(path, "r") as file:
            return file.read()


class OverwriteFileSkill(SafePathSkill):
    description = "Overwrite the content of a file."

    def execute(
        self,
        path: Annotated[str, "Path of file to overwrite"],
        content: Annotated[str, "Content to write to file"],
    ) -> str:
        """Overwrite the content of a file"""
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

        return f"File successfully overwritten"


class FileAction(Enum):
    WRITE = "+"
    REMOVE = "-"


@dataclass
class FileChange:
    action: Annotated[FileAction, "The action to perform on the file"]
    line_number: Annotated[int, "The line number to perform the action on"]
    content: Annotated[str, "The content to write to the specified line"]


class ModifyFileSkill(SafePathSkill):
    description = "Modify the content of a file."
    raise_on_404 = True

    def execute(
        self,
        path: Annotated[str, "Path of file to modify"],
        changes: Annotated[list[FileChange], "List of changes to apply to the file"],
    ) -> str:
        """Modify the content of a file"""
        with open(path, "r") as file:
            lines = file.readlines()

        changes = sorted(changes, key=lambda x: (x.line_number, list(FileAction).index(x.action)), reverse=True)
        for change in changes:
            if change.line_number < 1:
                raise ValueError("Invalid line number")

            if change.action == FileAction.WRITE:
                if change.line_number >= len(lines):
                    lines.extend([""] * (change.line_number - len(lines)))

                if not change.content.endswith("\n"):
                    change.content += "\n"
                lines[change.line_number - 1] = change.content

            if change.action == FileAction.REMOVE:
                lines.pop(change.line_number - 1)

        with open(path, "w") as file:
            file.writelines(lines)

        return f"File successfully modified"


class DeleteFileOrDirSkill(SafePathSkill):
    description = "Delete a file or directory."
    raise_on_404 = True

    def execute(self, path: Annotated[str, "Path of file or directory to delete"]) -> str:
        """Delete a file or directory"""
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)

        return f"{path} successfully deleted"


class CodingSkillSet(SkillSet):
    def __init__(self, work_dir: str) -> None:
        self.work_dir = work_dir
        super().__init__()

    @property
    def skill_set(self):
        return [ListDirSkill, ReadFileSkill, OverwriteFileSkill, ModifyFileSkill, DeleteFileOrDirSkill]

    def init_skills(self) -> list[Skill]:
        return [skill(work_dir=self.work_dir) for skill in self.skill_set]
