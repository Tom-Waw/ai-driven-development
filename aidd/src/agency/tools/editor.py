import shutil
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import Annotated, List

import pytest
from agency.tools import utils
from langchain.tools import BaseTool
from settings import settings

def format_lines(content: str) -> str:
    return "\n".join([f"{i + 1: >3}| {line}" for i, line in enumerate(content.splitlines())])

### CREATE ###


class CreateDir(BaseTool):
    name = "Directory Creation Tool"
    description: str = "Create an empty directory relative to the working directory."

    def _run(self, path: str) -> str:
        full_path = utils.validate_path(path)
        full_path.mkdir(parents=True)
        return f"Directory {path} created."


class CreateFile(BaseTool):
    name: str = "File Creation Tool"
    description: str = "Create an empty file relative to the working directory."

    def _run(self, path: str) -> str:
        full_path = utils.validate_path(path)
        full_path.touch()
        return f"File {path} created."


### READ ###


class ListDir(BaseTool):
    name: str = "Directory Listing Tool"
    description: str = dedent(
        """List the items of a directory in the working directory.
        Shows working directory if no path is provided."""
    )

    def _run(self, path: str) -> str:
        full_path = utils.validate_path(path)
        listing = "\n".join([p.name for p in full_path.iterdir()])
        if listing:
            return listing

        return f"Directory {path} is empty."


class ShowDirTree(BaseTool):
    name: str = "Directory Tree Tool"
    description: str = dedent(
        """Shows a tree representation of a directory in the working directory.
        Shows working directory if no path is provided."""
    )

    def _run(self, path: str) -> str:
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


class ReadFile(BaseTool):
    name: str = "File Reading Tool"
    description: str = "Read the entire content of a file in the working directory."

    def _run(self, path: str) -> str:
        full_path = utils.validate_path(path)
        content = full_path.read_text()
        if content:
            return format_lines(content)

        return f"File {path} is empty."


### UPDATE ###


class WriteContent(BaseTool):
    name: str = "File Content Writing Tool"
    description: str = dedent(
        """
        Write to a file in the working directory.

        You can use this tool to:
        - Overwrite a part or the entire content of a file.
        - Insert new content at a specific line number. (use start_line=end_line)
        - Remove content from file. (empty new_content and start_line<end_line)

        NOTES:
        - The line numbers are 1-based.
        - Having start_line=end_line will insert new content at the start_line.
        - Having start_line<end_line will remove content from start_line to end_line (exclusive).
        - You can provide multiple lines of content with line breaks to insert.
        - Indentation and line breaks are mandatory for multi-line content.

        CAUTION: Always check the content before the modification.
        """
    )

    def _run(
        self,
        path: str,
        start_line: Annotated[int, "The line number to start the modification."],
        end_line: Annotated[int, "The line number to end, exclusive from modification."],
        new_content: str,
    ) -> str:
        start_line -= 1
        end_line -= 1

        if start_line < 0 or end_line < 0:
            raise ValueError("Line numbers must be positive integers starting from 1.")

        if start_line > end_line:
            raise ValueError("Start line number must be smaller than end line number.")

        full_path = utils.validate_path(path)
        content = full_path.read_text()

        lines = content.splitlines()
        lines[start_line:end_line] = new_content.splitlines()
        content = "\n".join(lines)

        full_path.write_text(content)

        modified_content = format_lines(content)

        return f"""\
Content of {path} overwritten from line {start_line} to {end_line}

File Content
------------
{modified_content}"""


class MovePath(BaseTool):
    name: str = "Path Moving Tool"
    description: str = "Move a file or directory through the working directory."

    def _run(self, source: str, destination: str) -> str:
        full_src = utils.validate_path(source)
        full_dst = utils.validate_path(destination)
        shutil.move(full_src, full_dst)

        return f"Path {source} moved to {destination}."


### DELETE ###


class DeletePath(BaseTool):
    name: str = "Path Deletion Tool"
    description: str = dedent(
        """
        Delete a file or directory in the working directory.

        CAUTION: Deletes directory recursively with all content.
        """
    )

    def _run(self, path: Annotated[str, "The relativ path of the file or directory to delete."]) -> str:
        full_path = utils.validate_path(path)
        if full_path.is_file():
            full_path.unlink()
        else:
            shutil.rmtree(full_path)

        return f"Path {path} deleted."


### RUN ###


class CLICommand(BaseTool):
    name: str = "CLI Command Tool"
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

    def _run(self, command: Annotated[str, "The command to execute."]) -> str:
        if command.startswith("pytest") or command.startswith("pip"):
            return self._execute_command(command)

        user_response = input(f"Execute command:\n{command}\n\nEnter 'y' to confirm: ")
        if user_response.lower() == "y":
            return self._execute_command(command)

        return f"Command execution aborted.\nResponse:\n{user_response}"

    def _execute_command(self, command: str) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, cwd=settings.project_dir)
        output = result.stdout.decode()
        return f"Command executed with result:\n{output}"


class RunCode(BaseTool):
    name: str = "App Run Tool"
    description: str = "Start the application with a hint on what to do or look for."

    def _run(self, hint: Annotated[str, "A hint for the runner, what to do or look for."]) -> str:
        print(f"Developer asking to run code with hint:\n{hint}")
        result = input("Enter the result of the code execution: ")

        return f"Code executed with result:\n{result}"


# class TestExecution(BaseTool):
#     name: str = "Test Execution Tool"
#     description: str = dedent(
#         """Run tests to confirm the functionality of the code.
#         Leave the tests empty to run all tests in the working directory."""
#     )

#     def _run(self, tests: Annotated[List[str], "The paths to the tests to execute."]) -> str:
#         valid_paths = [utils.validate_path(test) for test in tests]

#         # Run the tests using pytest
#         buffer = StringIO()
#         with redirect_stdout(buffer):
#             pytest.main(["--rootdir", settings.project_dir, "-p", "no:cacheprovider", *valid_paths])
#         result = buffer.getvalue()

#         return f"Tests executed with result:\n{result}"
