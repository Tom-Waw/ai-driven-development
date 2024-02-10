from multiprocessing import managers

import autogen

from agents.config import base_config
from skills.io_skills import io_skills


def main():
    # ? Create the agents
    programmer = autogen.AssistantAgent(
        name="programmer",
        system_message="For coding tasks, only use the functions you have been provided with.",
        llm_config=base_config,
    )

    product_manager = autogen.AssistantAgent(
        name="product_manager",
        system_message="""
            You break down the requirements and the features of the product.
            You create the tasks, that have to be done, and assign them to the programmer.
            Be as specific as possible when assigning tasks.
            Reply TERMINATE when the task is done at full satisfaction.
            After the programmer has finished the task, you can ask for changes or improvements or you can terminate the task.
        """,
        llm_config=base_config,
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "work_dir": "output",
            "use_docker": False,
        },
    )

    # ? Register the skills
    for skill, description in io_skills:
        autogen.agentchat.register_function(
            skill,
            caller=programmer,
            executor=user_proxy,
            description=description,
        )

    groupchat = autogen.GroupChat(agents=[programmer, product_manager, user_proxy], messages=[])
    manager = autogen.GroupChatManager(groupchat, llm_config=base_config)

    # ? Start the conversation
    TASK = """
        Create the files to start a FastAPI server with the following endpoints:
        - GET /: Returns a JSON with the message "Hello, World!"
        - GET /items: Returns a JSON with a list of items
        - POST /items: Adds an item to the list
    """
    user_proxy.initiate_chat(manager, message=TASK)


if __name__ == "__main__":
    main()
