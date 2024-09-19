import json

from agency.lpu.standard import base_config
from autogen import Agent, AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent
from state.sprint import Sprint, Ticket

planning_proxy = UserProxyAgent(
    name="SprintPlan",
    human_input_mode="NEVER",
    code_execution_config=False,
)

planner = AssistantAgent(
    name="SoftwarePlanner",
    llm_config=base_config,
    system_message="""\
You are the project planner, responsible for task deconstruction via sprint planning.
You have the authority to manage sprints and tickets to ensure the project is on track.
Break down the project description into manageable milestones to validate the development team's progress.

Given a project description, your task is to break it down into milestones and plan the sprints accordingly.
After the development team has completed the sprint, you will be given a sprint review to evaluate the progress.
Given that review and the client's requirements, you will adjust the project plan accordingly and initiate the next sprint.

When planning a sprint, take the client's requirements and the former sprint reviews into account.

The Tickets will be executed in the order they are added to the sprint.
Make a plan of the next sprint before adding tickets to it.
Before submitting the sprint plan, ask the user to review your idea and goal for the sprint.
You need to get the user's approval before submitting the sprint plan.""",
)


### Tools ###


def validate_sprint(sprint: Sprint | None) -> None:
    if sprint is None:
        raise ValueError("Sprint plan not initialized.")


new_sprint: Sprint | None = None


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Initialize planning a new sprint with a goal.")
def init_sprint_plan(goal: str) -> str:
    global new_sprint
    # Update object
    new_sprint = Sprint(goal=goal)

    return "Sprint plan initialized."


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Abort the current sprint planning, removing all tickets.")
def abort_sprint_plan() -> str:
    global new_sprint
    new_sprint = None

    return "Sprint plan aborted."


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Show the current version of the sprint plan.")
def show_sprint_plan() -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    return f"""\
Current Sprint Plan
-------------------
{new_sprint.model_dump_json(indent=2)}"""


@planning_proxy.register_for_execution()
@planner.register_for_llm(
    description="Add a ticket to the current sprint. Optionally specify the position in the sprint."
)
def add_ticket(ticket: Ticket, position: int = -1) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    new_sprint.tickets.insert(position, ticket)

    return f"Ticket added.\n\n{show_sprint_plan()}"


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Remove a ticket from the current sprint.")
def remove_ticket(position: int) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    new_sprint.tickets.pop(position)

    return f"Ticket removed.\n\n{show_sprint_plan()}"


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Update a ticket in the current sprint.")
def update_ticket(position: int, ticket: Ticket) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    new_sprint.tickets[position] = ticket

    return f"Ticket updated.\n\n{show_sprint_plan()}"


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Move a tickets position in the current sprint.")
def move_ticket(position: int, new_position: int) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    ticket = new_sprint.tickets.pop(position)
    new_sprint.tickets.insert(new_position, ticket)

    return f"Ticket moved.\n\n{show_sprint_plan()}"


approval_requested = False


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Submit the final sprint plan for approval by the user.")
def submit_sprint_plan() -> str:
    global approval_requested
    approval_requested = True

    print(
        f"""\
USER APPROVAL REQUESTED
-----------------------
{show_sprint_plan()}"""
    )

    return "Sprint plan submitted for approval."


### Group Chat ###

user = UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    code_execution_config=False,
)


def speaker_selection(last_speaker: Agent, groupchat: GroupChat) -> Agent | None:
    global approval_requested
    if approval_requested:
        approval_requested = False
        return user

    if last_speaker == planner:
        return planning_proxy

    return planner


planning_group = GroupChat(
    agents=[user, planning_proxy, planner],
    messages=[],
    max_round=100,
    speaker_selection_method=speaker_selection,
)
chat_manager = GroupChatManager(
    groupchat=planning_group,
)


### Main Functions ###


def init_planners(request: str) -> None:
    planner.update_system_message(
        f"""\
{planner.system_message}

The following is the project you are working on.

Project Request
---------------
{request}"""
    )


def plan_sprint(iteration: int) -> Sprint | None:
    global new_sprint
    # Reset result object
    new_sprint = None

    if iteration > 1:
        # Review Previous Sprint
        chat_manager.initiate_chat(
            recipient=user,
            clear_history=False,
            max_turns=1,
            message="Before starting the next sprint planning, provide a detailed review of the previous sprint.",
        )

    # Plan Sprint
    chat_manager.initiate_chat(
        recipient=planner,
        clear_history=False,
        max_turns=100,
        message=f"Start planning sprint {iteration}. If you are happy with the sprint plan, get the user's approval.",
    )

    # Retrieve result object
    return new_sprint
