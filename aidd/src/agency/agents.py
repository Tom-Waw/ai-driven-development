import client_request
from agency.lpu.standard import base_config, is_termination_message
from autogen import AssistantAgent

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

software_designer = AssistantAgent(
    name="software_designer",
    llm_config=base_config,
    system_message=f"""
You are a Software Designer.
You excel in designing software applications and laying out the architecture.
Your responsibility is to plan the application and write a detailed design document.
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
