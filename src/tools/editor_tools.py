import shutil
from enum import Enum
from pickle import APPEND
from typing import Annotated, List, Optional

from pydantic import BaseModel
from regex import F

from ram import editor
from utils import dir_tree, format_lines

### CREATE ###


def create_dir(rel_path: Annotated[str, "The path of the directory to create."]) -> str:
    """Create a directory in the working directory."""
    path = editor.validate_rel_path(rel_path)
    path.mkdir(parents=True)
    return f"Directory {path} created."


def create_file(rel_path: Annotated[str, "The path of the file to create."]) -> str:
    """Create a file in the working directory."""
    path = editor.validate_rel_path(rel_path)
    path.touch()
    return f"File {path} created."


### READ ###


def show_dir_tree(rel_path: Annotated[str, "The path of the directory to show as a tree."] = "") -> str:
    """Shows a tree representation of a directory in the working directory.
    If no path is provided, the working directory is shown."""
    path = editor.validate_rel_path(rel_path)
    tree = dir_tree(path)
    return "\n".join(tree)


def list_dir(rel_path: Annotated[str, "The path of the directory to list."] = "") -> str:
    """List the content of a directory in the working directory.
    If no path is provided, the working directory is shown."""
    path = editor.validate_rel_path(rel_path)
    return "\n".join([p.name for p in path.iterdir()])


def read_file(rel_path: Annotated[str, "The path of the file to read."]) -> str:
    """Read the content of a file in the working directory."""
    path = editor.validate_rel_path(rel_path)

    with open(path, "r") as file:
        lines = file.readlines()

    # Add line numbers
    return format_lines(list(enumerate(lines)))


### UPDATE ###


def overwrite_file(
    rel_path: Annotated[str, "The path of the file to overwrite."],
    content: Annotated[str, "The content to write to the file."],
) -> str:
    """Overwrite the content of a file in the working directory."""
    path = editor.validate_rel_path(rel_path)

    with open(path, "w") as file:
        file.write(content)

    return f"File {path} overwritten."


class FileOperation(str, Enum):
    INSERT = "insert"
    APPEND = "append"
    DELETE = "delete"


class FileChange(BaseModel):
    operation: Annotated[
        FileOperation, "The operation to perform. Inserting before a line, appending after a line, or deleting lines."
    ]
    line_number: Annotated[int, "The line number to perform the operation on."]
    content: Annotated[Optional[str], "The content to insert or append. Always include proper indentation."] = None


def modify_file(
    rel_path: Annotated[str, "The path of the file to modify."],
    changes: Annotated[List[FileChange], "The changes to apply to the file."],
) -> str:
    """Modify a file in the working directory by inserting, appending, or deleting lines."""
    path = editor.validate_rel_path(rel_path)

    with open(path, "r") as file:
        lines = file.readlines()

    # Validate changes
    for change in changes:
        if change.line_number <= 0 or change.line_number > len(lines) + 1:
            raise ValueError("Invalid line number")
        if change.operation == FileOperation.DELETE and change.content:
            raise ValueError("Content should not be provided for delete operations.")
        if change.operation != FileOperation.DELETE and not change.content:
            raise ValueError("Content is required for insert and append operations.")

    # Sort changes
    changes.sort(key=lambda c: (c.line_number, c.operation), reverse=True)

    for change in changes:
        if change.operation == FileOperation.DELETE:
            lines.pop(change.line_number - 1)
            continue

        if not change.content:
            continue

        if change.operation == FileOperation.APPEND:
            insert = lambda l: lines.insert(change.line_number, l + "\n")
        elif change.operation == FileOperation.INSERT:
            insert = lambda l: lines.insert(change.line_number - 1, l + "\n")

        new_lines = change.content.split("\n")
        for line in reversed(new_lines):
            insert(line)

    with open(path, "w") as file:
        file.writelines(lines)

    from_line = max(0, changes[0].line_number - 2)
    to_line = min(
        len(lines), changes[-1].line_number + 3 + (len(changes[-1].content.split("\n")) if changes[-1].content else 0)
    )

    indizes = range(from_line, to_line)
    loi = list(zip(indizes, lines[from_line:to_line]))
    return f"File {path} modified.\n\n" + format_lines(loi)


def insert_before_line(
    rel_path: Annotated[str, "The path of the file to append to."],
    line_number: Annotated[int, "The line number to insert before."],
    content: Annotated[str, "The content to insert. Remember to include proper indentation."],
) -> str:
    """Insert content before a line in a file in the working directory. Proper indentation is important.
    This functions alters the file content, so always wait for the confirmation message before proceeding."""
    path = editor.validate_rel_path(rel_path)

    with open(path, "r") as file:
        lines = file.readlines()

    if line_number <= 0 or line_number > len(lines) + 1:
        raise ValueError("Invalid line number")

    new_lines = content.split("\n")
    for line in reversed(new_lines):
        lines.insert(line_number - 1, line + "\n")

    with open(path, "w") as file:
        file.writelines(lines)

    from_line = max(0, line_number - 2)
    to_line = min(len(lines), line_number + 3)

    indizes = range(from_line, to_line)
    loi = list(zip(indizes, lines[from_line:to_line]))
    return f"Content appended to file {path} at line {line_number}.\n\n" + format_lines(loi)


### DELETE ###


def delete(rel_path: Annotated[str, "The path of the file or directory to delete."]) -> str:
    """Delete a file or directory in the working directory. Deletes all content if a directory."""
    path = editor.validate_rel_path(rel_path)

    if path.is_dir():
        shutil.rmtree(path)
        return f"Directory {path} deleted."
    else:
        path.unlink()
        return f"File {path} deleted."
