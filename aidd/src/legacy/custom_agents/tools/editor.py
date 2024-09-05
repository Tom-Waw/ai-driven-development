from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import Field
from tools import utils
from tools.abc import Tool

tools: list[type[Tool]] = []


def register_tool(tool: type[Tool]) -> type[Tool]:
    tools.append(tool)
    return tool


class PathTool(Tool, ABC):
    """A tool that takes a path as input."""

    def call(self) -> str:
        valid_path = utils.validate_path(self.path)
        return self.call_validated(full_path=valid_path)

    @abstractmethod
    def call_validated(self, full_path: Path) -> str: ...


### CREATE ###


@register_tool
class CreateDir(PathTool):
    """Create a directory in the working directory."""

    path: str = Field(description="The relativ path of the directory to create.")

    def call_validated(self, full_path: Path) -> str:
        full_path.mkdir(parents=True)
        return f"Directory {self.path} created."


@register_tool
class CreateFile(PathTool):
    """Create a file in the working directory."""

    path: str = Field(description="The relativ path of the file to create.")

    def call_validated(self, full_path: Path) -> str:
        full_path.touch()
        return f"File {self.path} created."


### READ ###


@register_tool
class ListDir(PathTool):
    """List the content of a directory in the working directory.
    If no path is provided, the working directory is shown."""

    path: str | None = Field(None, description="The relativ path of the directory to list.")

    def call_validated(self, full_path: Path) -> str:
        listing = "\n".join([p.name for p in full_path.iterdir()])
        if listing:
            return listing

        return f"Directory {self.path} is empty."


# @register_tool
class ShowDirTree(PathTool):
    """Shows a tree representation of a directory in the working directory.
    If no path is provided, the working directory is shown."""

    path: str | None = Field(None, description="The relativ path of the directory to show as a tree.")

    def call_validated(self, full_path: Path) -> str:
        indentation = " " * 2

        def xml_dir_tree(current: Path, indent: int = 0) -> str:
            name = current.name if current != full_path else "."
            prefix = indentation * indent

            if current.is_file():
                return f"{prefix}<file name='{name}'/>"

            content = "\n".join([xml_dir_tree(subpath, indent=indent + 1) for subpath in current.iterdir()])
            if not content:
                return f"{prefix}<dir name='{name}' empty />"

            return f"{prefix}<dir name='{name}'>\n{content}\n{prefix}</dir>"

        return xml_dir_tree(full_path)


@register_tool
class ReadFile(PathTool):
    """Read the content of a file in the working directory."""

    path: str = Field(description="The relativ path of the file to read.")

    def call_validated(self, full_path: Path) -> str:
        content = full_path.read_text()
        if content:
            return content

        return f"File {self.path} is empty."


### UPDATE ###


@register_tool
class OverwriteContent(PathTool):
    """Overwrite the content of a file in the working directory.
    Replacing a specific content with new content.
    Indentation and line breaks are mandatory for multi-line content."""

    path: str = Field(description="The relativ path of the file to modify.")
    original_content: str = Field(description="The content to replace.")
    modify_content: str = Field(description="The new content.")

    def call_validated(self, full_path: Path) -> str:
        content = full_path.read_text()
        new_content = content.replace(self.original_content, self.modify_content)
        if content == new_content:
            return f"Content of {self.path} unchanged."

        full_path.write_text(new_content)
        return f"Content of {self.path} overwritten."


### DELETE ###


@register_tool
class DeletePath(PathTool):
    """Delete a file or directory in the working directory."""

    path: str = Field(description="The relativ path of the file or directory to delete.")

    def call_validated(self, full_path: Path) -> str:
        full_path.unlink()
        return f"Path {self.path} deleted."