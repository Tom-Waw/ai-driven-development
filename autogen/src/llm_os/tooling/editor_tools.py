from pathlib import Path
from typing import Annotated

from llm_os.ram import editor
from llm_os.tooling.registry import ToolRegistry

editor_tool_registry = ToolRegistry("editor_tools")

### CREATE ###


@editor_tool_registry.register
def create_dir(path: Annotated[Path, "The path of the directory to create."]) -> str:
    """Create a directory in the working directory."""
    editor.create_dir(path)
    return f"Directory {path} created."


@editor_tool_registry.register
def create_file(path: Annotated[Path, "The path of the file to create."]) -> str:
    """Create a file in the working directory."""
    editor.create_file(path)
    return f"File {path} created."


### READ ###


@editor_tool_registry.register
def show_dir_tree(path: Annotated[Path | None, "The path of the directory to show as a tree."] = None) -> str:
    """Shows a tree representation of a directory in the working directory.
    If no path is provided, the working directory is shown."""
    return editor.show_dir_tree(path)


@editor_tool_registry.register
def list_dir(path: Annotated[Path | None, "The path of the directory to list."] = None) -> str:
    """List the content of a directory in the working directory.
    If no path is provided, the working directory is shown."""
    return editor.list_dir(path)


@editor_tool_registry.register
def read_file(path: Annotated[Path, "The path of the file to read."]) -> str:
    """Read the content of a file in the working directory."""
    return editor.read_file(path)


### UPDATE ###


@editor_tool_registry.register
def overwrite_content(
    path: Annotated[Path, "The path of the file to modify."],
    overwrite_content: Annotated[str, "The content to replace."],
    new_content: Annotated[str, "The new content."],
) -> str:
    """Overwrite the content of a file in the working directory.
    Replacing a specific content with new content.
    Indentation and newlines are mandatory for multi-line content."""
    editor.overwrite_content(path, overwrite_content, new_content)
    return f"Content of {path} modified."


### DELETE ###


@editor_tool_registry.register
def delete(path: Annotated[Path, "The path of the file or directory to delete."]) -> str:
    """Delete a file or directory in the working directory. Deletes all content if a directory."""
    editor.delete(path)
    return f"{path} deleted."
