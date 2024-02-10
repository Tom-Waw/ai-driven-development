import os
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Annotated, Callable, List

from settings import Settings


@staticmethod
def safe_path(check_path=False):
    def decorator(method):
        @wraps(method)
        def wrapper(path, *args, **kwargs):
            abs_path = os.path.abspath(os.path.join(Settings.WORK_DIR, path))

            if check_path and not os.path.exists(abs_path):
                raise ValueError("File does not exist")

            if not os.path.commonpath([abs_path, Settings.WORK_DIR]) == Settings.WORK_DIR:
                raise ValueError("Access denied: Attempted access outside of working directory")

            if os.path.islink(abs_path):
                raise ValueError("Security alert: Path is a symbolic link")

            return method(abs_path, *args, **kwargs)

        return wrapper

    return decorator


class FileAction(Enum):
    WRITE = "+"
    REMOVE = "-"


@dataclass
class FileChange:
    action: Annotated[FileAction, "The action to perform on the file"]
    line_number: Annotated[int, "The line number to perform the action on"]
    content: Annotated[str, "The content to write to the specified line"]


@safe_path(check_path=True)
def read_file(path: Annotated[str, "Path of file to read"]) -> str:
    """Read the content of a file"""
    with open(path, "r") as file:
        return file.read()


@safe_path()
def overwrite_file(
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


@safe_path(check_path=True)
def modify_file(
    path: Annotated[str, "Path of file to modify"],
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

        if change.action == FileAction.REMOVE and 0 < change.line_number <= len(lines):
            lines.pop(change.line_number - 1)

    with open(path, "w") as file:
        file.writelines(lines)

    return f"File modified, applied {len(changes)} changes"


@safe_path()
def delete_file_or_dir(path: Annotated[str, "Path of file or directory to delete"]) -> str:
    """Delete a file or directory"""
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)

    return "File deleted"


@safe_path(check_path=False)
def execute_python_script(path: Annotated[str, "Path of python script to execute"]) -> str:
    """Execute a python script"""
    with open(path, "r") as file:
        script = file.read()

    try:
        exec(script)
    except Exception as e:
        return f"Error: {e}"

    return "Script executed"


io_skills: list[tuple[Callable, str]] = [
    (read_file, "Read the full content of a file"),
    (
        overwrite_file,
        """
            Overwrite a file, erasing the previous content.
            Will create the file and its parent directories if they do not exist.
        """,
    ),
    (
        modify_file,
        """
            Modify the content of an exisitng file using a list of changes.
            The changes are applied in reversed order of their line number.
            You can use the FileAction enum to specify the action to perform on the file.
        """,
    ),
    (delete_file_or_dir, "Delete a file"),
    (execute_python_script, "Execute a python script"),
]
