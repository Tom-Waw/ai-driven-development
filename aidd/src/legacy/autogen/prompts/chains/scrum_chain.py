from agents import create_assistant
from llm_os.lpu.standard import is_termination_message
from llm_os.ram.project import Project
from llm_os.ram.ticket_system import TicketSystem
from prompts.abc import Template

from autogen import UserProxyAgent

class 


def run_project_planning_chain(project: Project) -> TicketSystem:
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
        code_execution_config=False,
    )
    assistant = create_assistant()

    results = user.initiate_chats(
        chat_queue=[
            {
                "recipient": assistant,
                "message": RequirementsTemplate.render(description=project_description),
                "max_turns": 1,
            },
        ]
    )
    


