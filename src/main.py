import shutil
from pathlib import Path

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

    project_manager = autogen.AssistantAgent(
        name="project_manager",
        system_message="""
            You are the project manager of a tech company. You are responsible for the success of the project and the team.

            You will receive a request from the client. Depending on the needs, you will plan the project.
            To get the best results, you will manage your team to develop in a test driven development (TDD) environment.
            That requires the end result to be well described before the development starts.

            After the planning, you will guide the development of the project. That means, you will introduce phases and tasks to the team.
            As each phase starts, you will explain the requirements and the features of the product to the developers.
            Divide the tasks into tickets and assign them to the team members.

            To confirm the code works as expected, run the tests with the given functions.
            Only after the tests pass and you are satisfied with the result, you can terminate the task.

            Leave the implementation to the developers. You will not interfere with the code.
            You are provided with a function that enables you to run the tests. Do not use any other functions.

            Do not show any appreciation in your messages.
            Reply TERMINATE when the task is done at full satisfaction.
        """,
        llm_config=base_config,
    )
    UnitTestSkillSet.register(caller=project_manager, executor=user_proxy)

    programmer = autogen.AssistantAgent(
        name="programmer",
        system_message="""
            You are the programmer of the team.
            You are provided with a suite of functions that enable you to write the code into the project directory.

            You will receive tickets (tasks) from the project manager and you have to implement the code.
            Make sure to strictly follow the design and interfaces the project manager has provided.
            Your code has to pass the tests written by the tester. You can change the code as many times as necessary.

            Make sure to understand the requirements of the current ticket.
        """,
        llm_config=base_config,
    )
    PipSkillSet.register(caller=programmer, executor=user_proxy)
    CodingSkillSet.register(Settings.CODE_DIR, caller=programmer, executor=user_proxy)

    tester = autogen.AssistantAgent(
        name="tester",
        system_message="""
            You are the tester of the team. You are responsible for the quality of the code.
            You are provided with a suite of functions that enable you to write the code into the test directory.
            Exclusively use the library unittest for testing.

            You will receive tickets (tasks) from the project manager and you have to implement tests for the code.
            Make sure to strictly follow the design and interfaces the project manager has provided.
            Cover the main requirements and edge cases.
        """,
        llm_config=base_config,
    )
    CodingSkillSet.register(Settings.TEST_DIR, caller=tester, executor=user_proxy)

    groupchat = autogen.GroupChat(agents=[project_manager, programmer, tester, user_proxy], messages=[], max_round=50)
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


def reset_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Clean the session directory
    reset_dir(Settings.CODE_DIR)
    reset_dir(Settings.TEST_DIR)

    # Start the conversation
    main()
