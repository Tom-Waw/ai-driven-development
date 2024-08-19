import traceback

from agents import create_assistant
from llm_os import ram
from llm_os.tooling.editor_tools import editor_tool_registry
from prompts.chains.planning_chain import run_project_planning_chain
from prompts.coding import CodingSystemPrompt

from autogen import UserProxyAgent

client_request = """
Create a mini game that allows the user to create a character.
The user can change the appearance of the character and give it a name.
There are three character types: warrior, mage, and rogue.
One can pick the character type and the character will have different stats based on the type.
Also each character type has unique weapons and armor to choose from.

The game should have a simple UI that allows the user to interact with the game.
Also the user should be able to save the character to a file and load it later or delete it.
"""


def main():
    ram.reset()

    # project = run_project_planning_chain(client_request)

    # TODO: Prompt Chain with user interaction, setting up the application
    # chains.run_system_setup(user, project)
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    developer = create_assistant("Developer", CodingSystemPrompt)
    editor_tool_registry.assign(user, developer)

    user.initiate_chat(
        recipient=developer,
        message=f"""
Given the following project description, start coding the application.
Terminate, if you think you have completed the task.

<project_description>
{client_request}
</project_description>
""",
        max_turns=20,
    )

    # TODO: Prompt Chain, agents prototyping the application
    # chains.run_prototyping(user, project)


if __name__ == "__main__":
    while True:
        try:
            input("Press Enter to start the conversation...")
            main()
        except KeyboardInterrupt:
            print("\nRestarting...")
        except Exception as e:
            print(traceback.format_exc())
