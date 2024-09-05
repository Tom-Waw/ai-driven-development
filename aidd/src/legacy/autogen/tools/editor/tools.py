from pathlib import Path
from typing import Annotated

from tools.editor.utils import valid_path
from tools.registry import ToolRegistry

editor = ToolRegistry()


### Create ###


@editor.register
@valid_path
def create_dir(path: Annotated[Path, "The path of the directory to create."]) -> str:
    """Create a directory in the working directory."""
    path.mkdir(parents=True)
    return f"Directory {path} created."


@editor.register
@valid_path
def create_file(path: Annotated[Path, "The path of the file to create."]) -> str:
    """Create a file in the working directory."""
    path.touch()
    return f"File {path} created."


### READ ###


@editor.register
@valid_path
def list_dir(path: Annotated[Path | None, "The path of the directory to list."] = None) -> str:
    """List the content of a directory in the working directory.
    If no path is provided, the working directory is shown."""
    return "\n".join([p.name for p in path.iterdir()])


@editor.register
@valid_path
def show_dir_tree(path: Annotated[Path | None, "The path of the directory to show as a tree."] = None) -> str:
    """Shows a tree representation of a directory in the working directory.
    If no path is provided, the working directory is shown."""
    indentation = " " * 2

    def xml_dir_tree(current: Path, indent: int = 0) -> str:
        name = current.name if current != path else "."
        prefix = indentation * indent

        if current.is_file():
            return f"{prefix}<file name='{name}'/>"

        content = "\n".join([xml_dir_tree(subpath, indent=indent + 1) for subpath in current.iterdir()])
        if not content:
            return f"{prefix}<dir name='{name}'/>"

        return f"{prefix}<dir name='{name}'>\n{content}\n{prefix}</dir>"

    return xml_dir_tree(path)


@editor.register
@valid_path
def read_file(path: Annotated[Path, "The path of the file to read."]) -> str:
    """Read the content of a file in the working directory."""
    return path.read_text()


### UPDATE ###


@editor.register
@valid_path
def overwrite_content(
    path: Annotated[Path, "The path of the file to modify."],
    overwrite_content: Annotated[str, "The content to replace."],
    new_content: Annotated[str, "The new content."],
) -> str:
    """Overwrite the content of a file in the working directory.
    Replacing a specific content with new content.
    Indentation and newlines are mandatory for multi-line content."""
    old_content = path.read_text()

    content = old_content.replace(overwrite_content, new_content)
    if content == old_content:
        raise ValueError(f"Content '{overwrite_content}' not found in file at path: {path}")

    path.write_text(content)

    return f"Content of {path} modified."


### RUN ###


@editor.register
def run_code(hint: Annotated[str, "A hint for the runner, what to run and how."]) -> str:
    """Start the program execution with the given hint."""
    print(f"Developer asking to run code with hint:\n{hint}")
    result = input("Enter the result of the code execution: ")

    return f"Code executed with result:\n{result}"


### DELETE ###


@editor.register
@valid_path
def delete(path: Annotated[Path, "The path of the file or directory to delete."]) -> str:
    """Delete a file or directory in the working directory. Deletes all content if a directory."""
    if path.is_dir():
        path.rmdir()
    else:
        path.unlink()

    return f"{path} deleted."
