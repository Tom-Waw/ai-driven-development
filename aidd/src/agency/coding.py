from collections.abc import Callable
from typing import Annotated

from agency.lpu.standard import base_config
from agency.tools.abc import CustomTool
from agency.tools.editor import (
    CLICommand,
    CreateDir,
    CreateFile,
    DeleteContent,
    DeletePath,
    MovePath,
    ReadFile,
    RunCode,
    ShowDirTree,
    WriteContent,
)
from agency.tools.ticket_system import ShowTickets
from agency.tools.utils import generate_langchain_tool_schema
from autogen import Agent, AssistantAgent, ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from state.project_state import ProjectState
from state.sprint import Sprint, SprintResult, Ticket, TicketStatus

coder = AssistantAgent(
    name="Coder",
    system_message=f"""\
You are a coder, equipped with the knowledge and the tools to write quality code.
Given a Ticket, you can find the best way to implement the requested feature in the code base.

Code Conventions
-----------------
{ReadFile().run("docs/CONVENTIONS.md")}

Before implementing a new ticket, always read the documentation files to understand the project structure.
Keep them up to date when implementing new features.""",
    llm_config=base_config,
)

editor_exit = False


def terminate_on_exit(msg: dict) -> bool:
    global editor_exit
    if editor_exit:
        # Reset the flag
        editor_exit = False
        return True
    return False


coding_proxy = UserProxyAgent(
    name="editor",
    human_input_mode="NEVER",
    is_termination_msg=terminate_on_exit,
    description="A file editor to manage files and directories.",
    default_auto_reply="If the ticket is complete, submit it.",
    code_execution_config=False,
)


class SubmitTicket(CustomTool):
    name: str = "submit_ticket"
    description: str = "Submit the ticket and exit the editor, when all changes are done."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run() -> str:
            if len(self.state.current_sprint.open_tickets) == 0:
                raise ValueError("No ticket to submit.")

            self.state.current_sprint.open_tickets[0].status = TicketStatus.DONE

            if len(self.state.current_sprint.open_tickets) == 0:
                return "Ticket submitted. Evaluate the sprint to finish."

            global editor_exit
            editor_exit = True
            return "Ticket submitted."

        return _run


class EvaluateSprint(CustomTool):
    name: str = "evaluate_sprint"
    description: str = "When all tickets are done, evaluate the sprint and give a retrospective."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run(
            retrospective: Annotated[str, "A retrospective of the sprint."],
            final_result: Annotated[bool, "Whether the project as a whole was finished within the sprint."],
        ) -> str:
            if len(self.state.current_sprint.open_tickets) > 0:
                raise ValueError("The sprint must be finished before evaluating.")

            self.state.sprint_history.append(
                SprintResult(
                    sprint_goal=self.state.current_sprint.goal,
                    retrospective=retrospective,
                    project_finished=final_result,
                )
            )
            self.state.current_sprint = None
            global editor_exit
            editor_exit = True
            return "Sprint evaluated."

        return _run


def init_coder(state: ProjectState) -> ConversableAgent:
    coder.update_system_message(
        f"""\
{coder.system_message}

Project Request
---------------
{state.client_request}"""
    )

    tools: list[CustomTool] = [
        ShowTickets(state=state),
        SubmitTicket(state=state),
        EvaluateSprint(state=state),
        CreateDir(),
        CreateFile(),
        MovePath(),
        DeletePath(),
        ReadFile(),
        CLICommand(),
        # RunCode(),
        DeleteContent(),
        WriteContent(),
    ]
    for tool in tools:
        coding_proxy.register_for_execution(name=tool.name)(tool.run)
        coder.register_for_llm(name=tool.name, description=tool.description)(tool.run)
        # tool_sig = generate_langchain_tool_schema(tool)
        # coder.update_tool_signature(tool_sig, is_remove=False)
        # coding_proxy.register_function({tool.name: tool._run})

    finished_sprint_count = len(state.sprint_history) - 1

    def coding_init_message(
        recipient: ConversableAgent,
        messages: list[dict] | None = None,
        sender: Agent | None = None,
        config: dict | None = None,
    ) -> str:
        nonlocal finished_sprint_count

        sprint_intro = ""
        if finished_sprint_count < len(state.sprint_history):
            finished_sprint_count = len(state.sprint_history)
            sprint_intro = f"""\
A new sprint has started. Solve the tickets you have been assigned to.
Always keep the sprint goal in mind and work towards it, to deliver the best possible result.
Check the Documentation files for advice on how to implement the features.

Current Sprint Goal
-------------------
{state.current_sprint.goal}
"""

        return f"""{sprint_intro}\
You received a new ticket assigned to you:
{state.current_sprint.open_tickets[0].model_dump_json(indent=4)}

Working Directory
-----------------
{ShowDirTree().run(".")}"""

    def summary_method(
        sender: ConversableAgent,
        recipient: ConversableAgent,
        summary_args: dict,
    ) -> str:
        return "The sprint is finished."

    coding_proxy.register_nested_chats(
        [
            {
                "recipient": coder,
                "clear_history": False,
                "message": coding_init_message,
                "summary_method": summary_method,
            }
        ],
        trigger=lambda agent: agent != coder,
    )

    return coding_proxy
