import shutil
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from textwrap import dedent

from crewai_tools import BaseTool
from settings import settings


class AccessDeniedError(Exception):
    pass


def validate_path(path: str | None = None):
    if path is None:
        path = "."

    if Path(path).is_absolute():
        raise AccessDeniedError(f"Access denied: Absolute path {path} is not allowed.")

    full_path = (settings.project_dir / path).resolve()
    if not full_path.is_relative_to(settings.project_dir):
        raise AccessDeniedError(f"Access denied: Attempted access outside of project directory at path: {path}")

    return full_path


def valid_path(*path_args: str):
    if not path_args:
        path_args = ["path"]

    def decorator(func: Callable):
        arg_names = func.__code__.co_varnames

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            args = list(args)
            pos_args = [arg for arg in arg_names if arg not in kwargs]
            try:
                for arg in path_args:
                    if arg in kwargs:
                        kwargs[arg] = validate_path(kwargs[arg])
                    else:
                        idx = pos_args.index(arg)
                        args[idx] = validate_path(args[idx])

            except AccessDeniedError as e:
                return str(e) + "\nTry again with a valid path."

            return func(self, *args, **kwargs)

        for arg in path_args:
            wrapper.__annotations__[arg] = str

        return wrapper

    return decorator


### CREATE ###


class CreateDir(BaseTool):
    name: str = "Directory Creation Tool"
    description: str = "Create a directory relative to the working directory."

    @valid_path("path")
    def _run(self, path: Path) -> str:
        path.mkdir(parents=True)
        return f"Directory {path} created."


class CreateFile(BaseTool):
    name: str = "File Creation Tool"
    description: str = "Create a file relative to the working directory."

    @valid_path("path")
    def _run(self, path: Path) -> str:
        path.touch()
        return f"File {path} created."


### READ ###


class ListDir(BaseTool):
    name: str = "Directory Listing Tool"
    description: str = (
        "List the content of a directory in the working directory. Shows working directory if no path is provided."
    )

    @valid_path("path")
    def _run(self, path: Path) -> str:
        listing = "\n".join([p.name for p in path.iterdir()])
        if listing:
            return listing

        return f"Directory {path} is empty."


class ShowDirTree(BaseTool):
    name: str = "Directory Tree Tool"
    description: str = (
        "Shows a tree representation of a directory in the working directory. Shows working directory if no path is provided."
    )

    @valid_path("path")
    def _run(self, path: Path) -> str:
        indentation = " " * 2

        def xml_dir_tree(current: Path, indent: int = 0) -> str:
            name = current.name if current != path else "."
            prefix = indentation * indent

            if current.is_file():
                return f"{prefix}<file name='{name}'/>"

            if current.name in settings.ignore_dirs:
                return f"{prefix}<dir name='{name}' hidden />"

            content = "\n".join([xml_dir_tree(subpath, indent=indent + 1) for subpath in current.iterdir()])
            if not content:
                return f"{prefix}<dir name='{name}' empty />"

            return f"{prefix}<dir name='{name}'>\n{content}\n{prefix}</dir>"

        return xml_dir_tree(path)


class ReadFile(BaseTool):
    name: str = "File Reading Tool"
    description: str = "Read the content of a file in the working directory."

    @valid_path("path")
    def _run(self, path: Path) -> str:
        content = path.read_text()
        if content:
            return content

        return f"File {path} is empty."


### UPDATE ###


class WriteContent(BaseTool):
    name: str = "File Content Writing Tool"
    description: str = dedent(
        """\
        Overwrite parts of content of a file in the working directory.
        Replacing a specific content with new content.
        Indentation and line breaks are mandatory for multi-line content."""
    )

    @valid_path("path")
    def _run(self, path: Path, original_content: str, modify_content: str) -> str:
        content = path.read_text()
        new_content = content.replace(original_content, modify_content, 1)
        if content == new_content:
            return f"Content of {path} unchanged."

        path.write_text(new_content)

        return f"Content of {path} overwritten."


class MovePath(BaseTool):
    name: str = "Path Moving Tool"
    description: str = "Move a file or directory inside the working directory."

    @valid_path("path", "new_path")
    def _run(self, path: Path, new_path: Path) -> str:
        shutil.move(path, new_path)

        return f"Path {path} moved to {new_path}."


### DELETE ###


class DeletePath(BaseTool):
    name: str = "Path Deletion Tool"
    description: str = "Delete a file or directory in the working directory."

    @valid_path("path")
    def _run(self, path: Path) -> str:
        path.unlink()
        return f"Path {path} deleted."
