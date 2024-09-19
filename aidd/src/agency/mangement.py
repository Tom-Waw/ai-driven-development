from collections.abc import Callable

from agency.lpu.standard import base_config
from agency.tools.abc import CustomTool
from agency.tools.ticket_system import (
    AddTicket,
    DeleteTicket,
    ReadTicketDetails,
    SetSprintGoal,
    ShowTickets,
    UpdateTicketStatus,
)
from agency.tools.utils import generate_langchain_tool_schema
from autogen import Agent, AssistantAgent, ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from state.project_state import ProjectState
from state.sprint import Sprint, SprintResult, Ticket

planner = AssistantAgent(
    name="SoftwarePlanner",
    system_message=f"""\
You are the project planner, responsible for the project planning and execution.
You have the authority to manage sprints and tickets to ensure the project is on track.

Given a project description, you are able to break it down into milestones and plan the sprints accordingly.
You can react to changes in the project scope and adjust the next sprint planning accordingly.

When planning a sprint, take the client's requirements and the current project state into account.
A ticket should always serve one of the following purposes:
- Documentation / Planning
- Implementation
- Testing
Prioritize Documentation / Planning over Testing and Testing over Implementation.
The Tickets will be executed in the order they are added to the sprint.
Plan your tickets before adding them to the sprint.
""",
    llm_config=base_config,
)

sprint_submitted = False


def terminate_on_sprint_submit(msg: dict) -> bool:
    global sprint_submitted
    if sprint_submitted:
        # Reset the flag
        sprint_submitted = False
        return True
    return False


sprint_plan_proxy = UserProxyAgent(
    name="sprint_plan",
    human_input_mode="NEVER",
    is_termination_msg=terminate_on_sprint_submit,
    description="A sprint planner to manage sprints and tickets.",
    default_auto_reply="If the sprint plan is complete, submit the sprint.",
    code_execution_config=False,
)


class SubmitSprint(CustomTool):
    name: str = "submit_sprint"
    description: str = "Submit the sprint plan, when all changes are done."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run() -> str:
            global sprint_submitted
            if len(self.state.current_sprint.tickets) < 1:
                raise ValueError("The sprint must have at least one ticket.")

            sprint_submitted = True
            return "Submitting the sprint plan."

        return _run


class FinishProject(CustomTool):
    name: str = "finish_project"
    description: str = "Abort sprint planning and declare the project finished."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run() -> str:
            self.state.finished = True

            global sprint_submitted
            sprint_submitted = True
            return "Submitting the sprint plan."

        return _run


def init_planner(state: ProjectState) -> ConversableAgent:
    planner.update_system_message(
        f"""\
{planner.system_message}

Project Request
---------------
{state.client_request}"""
    )

    # ? Update tools
    tools: list[CustomTool] = [
        SetSprintGoal(state=state),
        AddTicket(state=state),
        ShowTickets(state=state),
        ReadTicketDetails(state=state),
        UpdateTicketStatus(state=state),
        DeleteTicket(state=state),
        SubmitSprint(state=state),
    ]
    for tool in tools:
        sprint_plan_proxy.register_for_execution(name=tool.name)(tool.run)
        planner.register_for_llm(name=tool.name, description=tool.description)(tool.run)
        # tool_sig = generate_langchain_tool_schema(tool)
        # planner.update_tool_signature(tool_sig, is_remove=False)
        # sprint_plan_proxy.register_function({tool.name: tool._run})

    def planning_init_message(
        recipient: ConversableAgent,
        messages: list[dict] | None = None,
        sender: Agent | None = None,
        config: dict | None = None,
    ) -> str:
        history_msg = "This is the first sprint."
        if state.sprint_history:
            history_msg = state.model_dump_json(indent=4, include={"sprint_history"})

        return f"""\
You are planning the next sprint for the project.
Set a goal for the sprint and add tickets to reach set goal.

Sprint History
---------------
{history_msg}"""

    def summary_message(
        sender: ConversableAgent,
        recipient: ConversableAgent,
        summary_args: dict,
    ) -> str:
        return "The next sprint is planned and ready for execution."

    sprint_plan_proxy.register_nested_chats(
        [
            {
                "recipient": planner,
                "message": planning_init_message,
                "summary_method": summary_message,
            }
        ],
        trigger=lambda agent: agent != planner,
    )

    return sprint_plan_proxy
