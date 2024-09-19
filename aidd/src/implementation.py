import shutil
import subprocess
from pathlib import Path
from typing import Annotated

from agency.lpu.standard import base_config
from agency.tools import utils
from autogen import AssistantAgent, UserProxyAgent
from settings import settings
from state.sprint import Sprint, TicketStatus

editor_exit = False


def terminate_on_exit(msg: dict) -> bool:
    global editor_exit
    if editor_exit:
        return True
    return False


editor_proxy = UserProxyAgent(
    name="Editor",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=terminate_on_exit,
)

coder = AssistantAgent(
    name="Coder",
    llm_config=base_config,
    system_message=f"""\
You are a coder, equipped with the knowledge and the tools to write quality code.
Given a Ticket, you can find the best way to implement the requested feature in the code base.""",
)


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Submit the current state of the project as the final solution to the ticket.")
def submit_ticket() -> str:
    global editor_exit
    # Update object
    editor_exit = True

    return "Ticket submitted."


### Tools ###


### File Operations ###


def format_lines(content: str) -> str:
    return "\n".join([f"{i + 1: >3}| {line}" for i, line in enumerate(content.splitlines())])


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Read the content of a file.")
def read_file(path: str) -> str:
    full_path = utils.validate_path(path)
    content = full_path.read_text()
    if not content:
        return f"File {path} is empty."

    return f"""\
Content of {path}
----------------
{format_lines(content)}
<<EOF"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(
    description="Write content to a file. Replace old piece of code with new one. Proper indentation is important."
)
def modify_file(
    path: Annotated[str, "Path of the file to change."],
    start_line: Annotated[int, "Start line number to replace with new code."],
    end_line: Annotated[int, "End line number to replace with new code."],
    new_code: Annotated[str, "New piece of code to replace old code with. Remember about providing indents."],
) -> str:
    full_path = utils.validate_path(path)
    content = full_path.read_text()
    lines = content.splitlines()

    lines[start_line - 1 : end_line] = new_code.splitlines()
    new_content = "\n".join(lines)

    full_path.write_text(new_content)

    return f"""\
Content of {path} has been updated.

{read_file(path)}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(
    description="Create an new file, optionally with intial content. Good use to initialize with a template."
)
def create_file(path: str, initial_content: Annotated[str, "Initial content of the file."] = "") -> str:
    full_path = utils.validate_path(path)
    full_path.write_text(initial_content)

    return f"""\
File {path} created.

{show_dir_tree()}

{read_file(path)}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Delete the content of a file.")

### Directory Operations ###


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Show the directory tree of the project.")
def show_dir_tree() -> str:
    indentation = " " * 2

    def xml_dir_tree(current: Path, indent: int = 0) -> str:
        name = current.name if indent > 0 else "."
        prefix = indentation * indent

        if current.is_file():
            return f"{prefix}<file name='{name}'/>"

        if current.name in settings.ignore_dirs:
            return f"{prefix}<dir name='{name}' hidden />"

        nested = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name))
        content = "\n".join([xml_dir_tree(subpath, indent=indent + 1) for subpath in nested])
        if not content:
            return f"{prefix}<dir name='{name}' empty />"

        return f"{prefix}<dir name='{name}'>\n{content}\n{prefix}</dir>"

    return f"""\
Working Directory
-----------------
{xml_dir_tree(settings.project_dir)}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Create an empty directory.")
def create_dir(path: str) -> str:
    full_path = utils.validate_path(path)
    full_path.mkdir(parents=True)

    return f"""\
Directory {path} created.

{show_dir_tree()}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Move a file or directory to a new location.")
def move_path(source: str, destination: str) -> str:
    source_path = utils.validate_path(source)
    destination_path = utils.validate_path(destination)

    shutil.move(source_path, destination_path)

    return f"""\
{source} moved to {destination}.

{show_dir_tree()}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Delete a file or directory with all its content.")
def delete_path(path: str) -> str:
    full_path = utils.validate_path(path)
    if full_path.is_file():
        full_path.unlink()
    else:
        shutil.rmtree(full_path)

    return f"""\
{path} removed.

{show_dir_tree()}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(description="Pip install one or more packages. (separate by space or '-r requirements.txt')")
def pip_install(packages: str) -> str:
    result = subprocess.run(
        ["pip", "install", *packages.split()], capture_output=True, text=True, cwd=settings.project_dir
    )
    output = result.stdout or result.stderr
    return f"""\
Pip output
----------
{output}"""


@editor_proxy.register_for_execution()
@coder.register_for_llm(
    description="Run pytest for the project. Optionally provide paths to run tests for specific files."
)
def run_tests(paths: str = "") -> str:
    result = subprocess.run(["pytest", *paths.split()], capture_output=True, text=True, cwd=settings.project_dir)
    output = result.stdout or result.stderr
    return f"""\
Test output
-----------
{output}"""


### Main Functions ###


def init_developers(request: str) -> None:
    coder.update_system_message(
        f"""\
{coder.system_message}

The following is the project you are working on.
Always focus on the scope of the ticket you are working on.

Project Request
---------------
{request}"""
    )


def run_implementation(sprint: Sprint) -> None:
    """Execute all tickets of the current sprint. When all tickets are done, evaluate the sprint and give a retrospective."""
    global editor_exit

    sprint_intro_message = f"""\
A new sprint has started. Solve the tickets you have been assigned to.

Current Sprint Goal
-------------------
{sprint.goal}

"""

    for ticket in sprint.open_tickets:
        # Reset result object
        editor_exit = False
        editor_proxy.initiate_chat(
            recipient=coder,
            clear_history=False,
            max_turns=100,
            message=f"""{sprint_intro_message}\
You received a new ticket assigned to you:

Ticket
------
{ticket.model_dump_json(indent=2)}

This is a file editor to make the necessary changes to the code base.

{show_dir_tree()}""",
        )
        if editor_exit:
            ticket.status = TicketStatus.DONE
        else:
            ticket.status = TicketStatus.FAILED
