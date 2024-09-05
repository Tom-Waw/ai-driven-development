import client_request
from autogen import AssistantAgent
from lpu.standard import base_config, is_termination_message

project_manager = AssistantAgent(
    name="project_manager",
    llm_config=base_config,
    is_termination_msg=is_termination_message,
    system_message=f"""
You are the Project Manager of a software development team.
You excel in delegating tasks, modarating team meetings and managing project resources.
Your responsibility is to oversee the development of a software application.

The client has requested a software application (see <client_request>).
Your only task is to provide team members with information and guidance to complete the project.
Do not directly participate in the project development.

<client_request>
{client_request.SMALL}
</client_request>
        """,
)

software_engineer = AssistantAgent(
    name="software_engineer",
    llm_config=base_config,
    system_message=f"""
You are a Software Engineer in a software development team.
You excel in designing software applications and solving technical problems.
Your responsibility is to plan the application and create tickets for the developers.
You go through the project and gather information on, what changes have to be made for the current sprint.
You do not write code.
    """,
)

developer = AssistantAgent(
    name="developer",
    llm_config=base_config,
    system_message=f"""
You are a Developer in a software development team.
You excel in writing code and implementing software applications.
Your responsibility is to write code and test the application.
    """,
)
