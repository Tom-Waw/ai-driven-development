import shutil
import subprocess
from pathlib import Path
from textwrap import dedent
from typing import Annotated, Callable

from agency.tools import utils
from agency.tools.abc import CustomTool
from settings import settings

### File Operations ###


def format_lines(content: str) -> str:
    return "\n".join([f"{i + 1: >3}| {line}" for i, line in enumerate(content.splitlines())])


class ReadFile(CustomTool):
    name: str = "file_read_tool"
    description: str = "Read the entire content of a file in the working directory."

    @property
    def run(self) -> Callable:
        def _run(path: str) -> str:
            full_path = utils.validate_path(path)
            content = full_path.read_text()
            if not content:
                return f"File {path} is empty."

            return f"""\
Content of {path}
----------------
{format_lines(content)}
<<EOF"""

        return _run


### UPDATE ###


class WriteContent(CustomTool):
    name: str = "file_content_write_tool"
    description: str = dedent(
        """
        Write content to a file in the working directory at a specific line number (cursor position).

        NOTES:
        - You can provide multiple lines of content with line breaks.
        - Indentation and line breaks are mandatory for multi-line content.
        - The content will be written after the specified line number.
        -> Use cursor position 1 to prepend content at the beginning.
        -> Use last line number + 1 to append content at the end. (e.g. 5 for file with 4 lines)

        CAUTION: The previous content will not be overwritten.
        The new content will be added at beginning of specified cursor position.
        The previous content will be pushed down.
        """
    )

    @property
    def run(self) -> Callable:
        def _run(path: str, cursor_pos: int, new_content: str) -> str:
            cursor_pos -= 1
            if cursor_pos < 0:
                raise ValueError("Line number must be a positive integer.")

            full_path = utils.validate_path(path)
            content = full_path.read_text()

            lines = content.splitlines()
            lines.insert(cursor_pos, new_content)
            content = "\n".join(lines)

            full_path.write_text(content)

            return f"""\
Content written to {path} after line {cursor_pos}

{ReadFile().run(path)}"""

        return _run


class DeleteContent(CustomTool):
    name: str = "file_content_delete_tool"
    description: str = dedent(
        """
        Delete content from a file in the working directory.

        NOTES:
        - The line numbers are 1-based.
        - Will remove content from start_line to end_line. (end_line exclusive)

        CAUTION: The line at end_line will not be deleted.
        The start_line will be removed.
        """
    )

    @property
    def run(self) -> Callable:
        def _run(path: str, start_line: int, end_line: int) -> str:
            start_line -= 1
            end_line -= 1

            if start_line < 0 or end_line < 0:
                raise ValueError("Line numbers must be positive integers starting from 1.")

            if start_line >= end_line:
                raise ValueError("Start line number must be smaller than end line number.")

            full_path = utils.validate_path(path)
            content = full_path.read_text()

            lines = content.splitlines()
            del lines[start_line:end_line]
            content = "\n".join(lines)

            full_path.write_text(content)

            return f"""\
Content of {path} deleted from line {start_line} to {end_line}

{ReadFile().run(path)}"""

        return _run


### Directory Operations ###


class ShowDirTree(CustomTool):
    name: str = "directory_tree_tool"
    description: str = dedent(
        """
        Shows a tree representation of a directory in the working directory.
        Shows working directory if no path is provided."""
    )

    @property
    def run(self) -> Callable:
        def _run(path: str) -> str:
            full_path = utils.validate_path(path)

            indentation = " " * 2

            def xml_dir_tree(current: Path, indent: int = 0) -> str:
                name = current.name if indent > 0 else "."
                prefix = indentation * indent

                if current.is_file():
                    return f"{prefix}<file name='{name}'/>"

                if current.name in settings.ignore_dirs:
                    return f"{prefix}<dir name='{name}' hidden />"

                content = "\n".join([xml_dir_tree(subpath, indent=indent + 1) for subpath in current.iterdir()])
                if not content:
                    return f"{prefix}<dir name='{name}' empty />"

                return f"{prefix}<dir name='{name}'>\n{content}\n{prefix}</dir>"

            return xml_dir_tree(full_path)

        return _run


class CreateDir(CustomTool):
    name: str = "directory_create_tool"
    description: str = "Create an empty directory relative to the working directory."

    @property
    def run(self) -> Callable:
        def _run(path: str) -> str:
            full_path = utils.validate_path(path)
            full_path.mkdir(parents=True)
            return f"""\
Directory {path} created.

{ShowDirTree().run(".")}"""

        return _run


class CreateFile(CustomTool):
    name: str = "file_create_tool"
    description: str = "Create an empty file relative to the working directory."

    @property
    def run(self) -> Callable:
        def _run(path: str) -> str:
            full_path = utils.validate_path(path)
            full_path.touch()
            return f"""\
File {path} created.

{ShowDirTree().run(".")}"""

        return _run


class MovePath(CustomTool):
    name: str = "path_move_tool"
    description: str = "Move a file or directory through the working directory."

    @property
    def run(self) -> Callable:
        def _run(source: str, destination: str) -> str:
            full_src = utils.validate_path(source)
            full_dst = utils.validate_path(destination)
            shutil.move(full_src, full_dst)

            return f"""\
Path {source} moved to {destination}.

{ShowDirTree().run(".")}"""

        return _run


class DeletePath(CustomTool):
    name: str = "path_delete_tool"
    description: str = dedent(
        """
        Delete a file or directory in the working directory.

        CAUTION: Deletes directory recursively with all content.
        """
    )

    @property
    def run(self) -> Callable:
        def _run(path: Annotated[str, "The relativ path of the file or directory to delete."]) -> str:
            full_path = utils.validate_path(path)
            if full_path.is_file():
                full_path.unlink()
            else:
                shutil.rmtree(full_path)

            return f"""\
Path {path} deleted.

{ShowDirTree().run(".")}"""

        return _run


### RUN Operations ###


class CLICommand(CustomTool):
    name: str = "cli_tool"
    description: str = dedent(
        """
        Execute a command from the command line.

        NOTES:
        - The command will be executed in the working directory.
        - Use the provided tools where possible.
        - The command will be validated before execution.

        CAUTION: Strictly avoid interactive commands. 
        """
    )

    @property
    def run(self) -> Callable:
        def _run(command: Annotated[str, "The command to execute."]) -> str:
            if command.startswith("pytest") or command.startswith("pip"):
                return self._execute_command(command)

            user_response = input(f"Execute command:\n{command}\n\nEnter 'y' to confirm: ")
            if user_response.lower() == "y":
                return self._execute_command(command)

            return f"Command execution aborted.\nResponse:\n{user_response}"

        return _run

    def _execute_command(self, command: str) -> str:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=settings.project_dir,
        )
        output = result.stdout or result.stderr
        return f"Command executed with result:\n{output}"


class RunCode(CustomTool):
    name: str = "app_run_tool"
    description: str = "Start the application with a hint on what to do or look for."

    @property
    def run(self) -> Callable:
        def _run(hint: Annotated[str, "A hint for the runner, what to do or look for."]) -> str:
            print(f"Developer asking to run code with hint:\n{hint}")
            result = input("Enter the result of the code execution: ")

            return f"Code executed with result:\n{result}"

        return _run
