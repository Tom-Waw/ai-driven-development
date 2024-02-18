from __future__ import annotations

import inspect
import os
import shutil
import stat
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Annotated, List, get_type_hints

from numpy import full

from settings import Settings
from skills.base import Skill, SkillSet


class SafePathSkill(Skill, ABC):
    raise_on_404 = False

    def __init__(self, work_dir: Path = Settings.CODE_DIR, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.work_dir = work_dir

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # Overwrite the execute method for the subclass
        execute = cls._overwrite_execute()
        setattr(cls, "execute", execute)

    @classmethod
    def _overwrite_execute(cls):
        sig = inspect.signature(cls.safe_execute)
        annotations = get_type_hints(cls.safe_execute, include_extras=True)
        annotations["path"].__origin__ = str

        path_param_index = list(sig.parameters).index("path")
        # Copy signature and update path default
        parameters = list(sig.parameters.values())
        prev = parameters[path_param_index]
        parameters[path_param_index] = prev.replace(
            annotation=annotations["path"],
            default=str(prev.default) if prev.default is not inspect.Parameter.empty else prev.default,
        )
        new_sig = sig.replace(parameters=parameters)

        print(new_sig)

        # New execute method for the subclass
        def execute(self: cls, *args, **kwargs):
            # Transform path argument
            bound_args = new_sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            path = bound_args.arguments["path"]
            full_path = self._validate_and_resolve_path(path)
            bound_args.arguments["path"] = full_path

            return cls.safe_execute(*bound_args.args, **bound_args.kwargs)

        # Apply annotations and signature to the new execute method
        execute.__annotations__ = annotations
        execute.__signature__ = new_sig
        return execute

    @abstractmethod
    def safe_execute(self, path: Annotated[Path, ...], *args, **kwargs): ...

    def execute(self, *args, **kwargs): ...

    def _validate_and_resolve_path(self, path: str) -> Path:
        full_path = self.work_dir / path

        if self.raise_on_404 and not full_path.exists():
            raise ValueError(f"File does not exist at path: {path}")

        # Check if path is inside the working directory with pathlib
        if not full_path.is_relative_to(self.work_dir):
            raise ValueError(f"Access denied: Attempted access outside of working directory at path: {path}")

        # Check if path is symbolic link
        if full_path.is_symlink():
            raise ValueError(f"Security alert: Path is a symbolic link at path: {path}")

        return full_path.resolve()


class ListDirSkill(SafePathSkill):
    description = "List the content of a directory."
    raise_on_404 = True

    def safe_execute(self, path: Annotated[Path, "Path of directory to list"] = Path("")) -> List[str]:
        """List the content of a directory"""
        return os.listdir(path)


class DirTreePrefix(str, Enum):
    SPACE = "    "
    BRANCH = "│   "
    # pointers:
    TEE = "├── "
    LAST = "└── "


class DirTreeSkill(Skill):
    description = "Get the full directory tree of the working directory. (all files and directories)"

    def __init__(self, work_dir: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.work_dir = work_dir

    def execute(self) -> str:
        """Get the full directory tree"""
        tree = self.rec_tree(self.work_dir)
        return "\n".join(tree)

    def rec_tree(self, dir_path: Path, prefix: str = ""):
        """Recursively get the full directory tree"""
        contents = list(dir_path.iterdir())
        pointers = [DirTreePrefix.TEE] * (len(contents) - 1) + [DirTreePrefix.LAST]
        for pointer, path in zip(pointers, contents):
            yield prefix + pointer.value + path.name
            if path.is_dir():
                extension = DirTreePrefix.BRANCH if pointer == DirTreePrefix.TEE else DirTreePrefix.SPACE
                yield from self.rec_tree(path, prefix=prefix + extension.value)


class ReadFileSkill(SafePathSkill):
    description = "Read the content of a file with line numbers."
    raise_on_404 = True

    def safe_execute(self, path: Annotated[Path, "Path of file to read"]) -> str:
        """Read the content of a file and return it with line numbers"""
        with open(path, "r") as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            lines[i] = f"{i+1}: {line}"

        return "".join(lines)


class CreateOrOverwriteFileSkill(SafePathSkill):
    description = "Create or overwrite a file."

    def safe_execute(
        self,
        path: Annotated[Path, "Path of file to create or overwrite"],
        content: Annotated[str, "Content to write to file"],
    ) -> str:
        """Create and overwrite a file"""
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

        return "File successfully written"


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

    def safe_execute(
        self,
        path: Annotated[Path, "Path of file to modify"],
        changes: Annotated[List[FileChange], "List of changes to apply to the file"],
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

    def safe_execute(self, path: Annotated[Path, "Path of file or directory to delete"]) -> str:
        """Delete a file or directory"""
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

        return f"{path} successfully deleted"


class CodingSkillSet(SkillSet):
    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir
        super().__init__()

    @property
    def skill_set(self):
        return [
            ListDirSkill,
            ReadFileSkill,
            CreateOrOverwriteFileSkill,
            ModifyFileSkill,
            DeleteFileOrDirSkill,
        ] + [DirTreeSkill]

    def init_skills(self) -> List[Skill]:
        return [skill(work_dir=self.work_dir) for skill in self.skill_set]
