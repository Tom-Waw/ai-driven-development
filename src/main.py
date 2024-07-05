from math import e
from pathlib import Path

import autogen

import ram
import tools
from config import task_config
from lpu.standard import PROMPT_APPRECIATION_CONSTRAINT, PROMPT_END_CONVERSATION, base_config, is_termination_message
from ram import editor
from tools import editor_tools, ticket_tools

# TODO: Build agents and teams / worklfows
# ? Create the agents
# ? Gather them in teams / workflows

# TODO: Create tools for agents
# ? Provide necessary tools
# ? Register the tools to the agents

# ! DONE
# TODO: Reset the development environment
# ? Reset session directory

# TODO: Arrange the conversation in workflows
# ? Define workflows
# ? Define termination
# ? Define transitions
# ? Assign the workflows to the teams

# ! DONE
# TODO: Start the conversation
# ? Load the task from yml
# ? Provide the task
# ? Start the conversation


def main():
    ram.reset()

    user = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
        code_execution_config=False,
    )

    assistant = autogen.AssistantAgent(
        name="Assistant",
        system_message="""You are a well trained professional software developer (python).
        You are able to solve any problem that comes your way.
        The provided functions suit you with the abilities to create and maintain software.
        Actively use them to persist your changes.
        Only terminate after reconfirming the files and directories you have created."""
        + PROMPT_END_CONVERSATION
        + PROMPT_APPRECIATION_CONSTRAINT,
        llm_config=base_config,
        is_termination_msg=is_termination_message,
    )
    for tool in [
        editor_tools.create_dir,
        editor_tools.create_file,
        editor_tools.show_dir_tree,
        editor_tools.list_dir,
        editor_tools.read_file,
        editor_tools.overwrite_file,
        editor_tools.remove_lines,
        editor_tools.insert_before_line,
        editor_tools.delete,
    ]:
        tools.register_tool(user, tool, assistant)

    documenter = autogen.AssistantAgent(
        name="Documenter",
        system_message="""You are a well trained professional software developer (python).
        You are able to solve any problem that comes your way.
        The provided functions suit you with the abilities to create and maintain software.
        Actively use them to persist your changes.
        Only terminate after reconfirming the files and directories you have edited."""
        + PROMPT_END_CONVERSATION
        + PROMPT_APPRECIATION_CONSTRAINT,
        is_termination_msg=is_termination_message,
        llm_config=base_config,
    )
    for tool in [
        editor_tools.show_dir_tree,
        editor_tools.list_dir,
        editor_tools.read_file,
        # editor_tools.overwrite_file,
        editor_tools.remove_lines,
        editor_tools.insert_before_line,
    ]:
        tools.register_tool(user, tool, documenter)

    CODING_TASK = task_config.load_task("character_game")
    CODING_TASK += "\n\n" + "For now just create the data models and classes for the game."
    DOCUMENTATION_TASK = """Your task is to reconfirm the code of the developer and document it.
    You can find it by checking the files in the session directory.
    Add Docstrings to the functions and classes for better understanding.
    You are done when you have documented all of the code.
    Check by reading the files and confirming the documentation."""

    user.initiate_chats(
        [
            {
                "recipient": assistant,
                "message": CODING_TASK,
                "summary_method": lambda *_: editor_tools.show_dir_tree(),
            },
            {
                "recipient": documenter,
                "message": DOCUMENTATION_TASK,
            },
        ]
    )

    ram.show()


if __name__ == "__main__":
    main()
