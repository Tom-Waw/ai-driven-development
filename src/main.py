import os
import shutil

import autogen

from agents.config import base_config
from settings import Settings
from skills.io_skills import CodingSkillSet
from skills.pip_skills import PipSkillSet
from skills.unit_test_skills import UnitTestSkillSet


def main():
    # ? Create the agents
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    )

    programmer = autogen.AssistantAgent(
        name="programmer",
        system_message="""
            For coding tasks, only use the functions you have been provided with.
            Write the code directly in the directory (don't create a project subdirectory).
            Remember to create __init__.py files in the directory.
            Do not create executable files, the python file should be the entry point.
            Python packages will be managed by the product manager.
        """,
        llm_config=base_config,
    )
    CodingSkillSet.register(Settings.CODE_DIR, caller=programmer, executor=user_proxy)

    tester = autogen.AssistantAgent(
        name="tester",
        system_message="""
            You test the code written by the programmer to make sure it works as expected.
            For that you create a test directory and write the test code there.
            Exclusively use the library unittest for testing. Remember to create __init__.py files in the test directory.
            Make sure to cover all the requirements and edge cases.
            If the code is not working or the requirements are not met, you can ask for changes or improvements.
            For testing, only use the functions you have been provided with.
        """,
        llm_config=base_config,
    )
    UnitTestSkillSet.register(caller=tester, executor=user_proxy)

    product_manager = autogen.AssistantAgent(
        name="product_manager",
        system_message="""
            You break down the requirements and the features of the product.
            Be as specific as possible when assigning tasks.
            For managing packages, only use the functions you have been provided with. Do not create a requirements.txt file.

            You create the tasks, that have to be done, and assign them to the programmer.
            After the programmer has finished the task, you can ask for changes or improvements or you can terminate the task.

            To confirm the code works as expected, consult the tester.
            Only after the tester has confirmed the code works, you can terminate the task.

            Make sure every aspect of the task is done correctly.
            Do not show any appreciation in your messages.
            Reply TERMINATE when the task is done at full satisfaction.
        """,
        llm_config=base_config,
    )
    PipSkillSet.register(caller=product_manager, executor=user_proxy)

    groupchat = autogen.GroupChat(agents=[programmer, tester, product_manager, user_proxy], messages=[], max_round=50)
    manager = autogen.GroupChatManager(groupchat, llm_config=base_config)

    # ? Start the conversation
    TASK = """
        Create the files to start a FastAPI server with the following endpoints:
        - GET /: Returns a JSON with the message "Hello, World!"
        - GET /items: Returns a JSON with a list of items
        - POST /items: Adds an item to the list
        - DELETE /items: Deletes all items from the list

        The task is done, when there is a tests directory with the tests for the server and the server is working as expected.
    """
    user_proxy.initiate_chat(manager, message=TASK)


if __name__ == "__main__":
    # Clean the output directory
    if os.path.exists("output"):
        shutil.rmtree("output")

    os.makedirs("output")

    # Start the conversation
    main()
