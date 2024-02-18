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
        code_execution_config=False,
    )

    product_manager = autogen.AssistantAgent(
        name="product_manager",
        system_message="""
            You break down the requirements and the features of the product.
            Be as specific as possible when assigning tasks.
            Plan out the project in detail and make sure the programmer understands the requirements.

            You create the tasks, that have to be done, and assign them to the appropriate person.
            The programmer has the responsibility to implement the code.
            The tester has the responsibility to test the code.

            To confirm the code works as expected, consult the tester.
            Only after the tester has confirmed the code works, you can terminate the task.

            Make sure every aspect of the task is done correctly.
            Do not show any appreciation in your messages.
            Reply TERMINATE when the task is done at full satisfaction.
        """,
        llm_config=base_config,
    )

    programmer = autogen.AssistantAgent(
        name="programmer",
        system_message="""
            Write the code directly in the directory (don't create a project subdirectory).
            Remember to create __init__.py files in the directory.

            You will receive the tasks from the product manager and you will have to implement the code.
            Make sure to follow the requirements and the features of the product.
            You can change the code as many times as you want until the product manager is satisfied.

            After the implementation of the code base is done, you will summarize the code for the tester.
            You will go back and forth with the tester to make sure the code is well structured and the interfaces are well defined.

            Only use the functions you have been provided with. Paths start inside the code directory.
        """,
        llm_config=base_config,
    )
    PipSkillSet.register(caller=programmer, executor=user_proxy)
    CodingSkillSet.register(Settings.CODE_DIR, caller=programmer, executor=user_proxy)

    tester = autogen.AssistantAgent(
        name="tester",
        system_message="""
            You test the code written by the programmer to make sure it works as expected.
            Exclusively use the library unittest for testing. Remember to create __init__.py files in the test directory.

            When the implementation of the code base is done, you will ask the programmmer to summarize the code.
            Ask for the basic structure, the classes, the functions and all the interfaces.
            Go back and forth with the programmer to make sure the code is well structured and the interfaces are well defined.

            After that, write the tests with the expected behavior of the code one by one.
            For each test, you will run it and check if it passes or fails. If it fails, you give feedback and provide the reason why it failed.

            Make sure to cover all the requirements and edge cases.
            Only use the functions you have been provided with. Paths start inside the testing directory.
            You cannot change the code, only the tests.
        """,
        llm_config=base_config,
    )
    UnitTestSkillSet.register(caller=tester, executor=user_proxy)

    groupchat = autogen.GroupChat(agents=[product_manager, programmer, tester, user_proxy], messages=[], max_round=50)
    manager = autogen.GroupChatManager(groupchat, llm_config=base_config)

    # ? Start the conversation
    TASK = """
        Create the files to start a FastAPI server with the following endpoints:
        - GET /: Returns a JSON with the message "Hello, World!"
        - GET /items: Returns a JSON with a list of items
        - POST /items: Adds an item to the list
        - DELETE /items: Deletes all items from the list
    """
    user_proxy.initiate_chat(manager, message=TASK)


def reset_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)


if __name__ == "__main__":
    # Clean the session directory
    reset_dir(Settings.CODE_DIR)
    reset_dir(Settings.TEST_DIR)

    # Start the conversation
    main()
