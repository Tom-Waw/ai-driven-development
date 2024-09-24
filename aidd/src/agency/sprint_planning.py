from agency.lpu.standard import base_config
from autogen import Agent, AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent
from sprint import Sprint, Ticket, TicketData

planning_proxy = UserProxyAgent(
    name="SprintPlan",
    human_input_mode="NEVER",
    code_execution_config=False,
)

planner = AssistantAgent(
    name="SoftwarePlanner",
    llm_config=base_config,
    system_message="""\
You are a Sprint Planning Agent.
In an agile software development project, you are responsible for planning the project's sprints.
Factor in the project description, the current state of the project and former sprint reviews to plan the next sprint.
Each sprint has to focus on a specific goal, and the tickets should be planned accordingly.

The order of the tickets in the sprint is important and will dictate the order of execution.

Instructions
------------
- think of the next state the project should be in after the sprint.
- formulate a goal for the sprint and initialize the sprint plan.
- think of the necessary tasks to achieve the goal and the order in which they should be executed.
- add tickets for each task to the sprint plan.
- review the sprint plan and make sure it aligns with the sprint goal.
- submit the sprint plan for approval by the user.
- factor in the user's feedback and adjust the sprint plan accordingly.""",
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
def add_ticket(ticket: TicketData, position: int = -1) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    ticket = Ticket.model_validate(ticket)
    new_sprint.tickets.insert(position, ticket)

    return f"Ticket added.\n\n{show_sprint_plan()}"


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Remove a ticket from the current sprint.")
def remove_ticket(id: int) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    ticket = new_sprint.get_ticket_by_id(id)
    if ticket is None:
        raise ValueError("Ticket not found.")
    new_sprint.tickets.remove(ticket)

    return f"Ticket removed.\n\n{show_sprint_plan()}"


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Update a ticket in the current sprint.")
def update_ticket(id: int, ticket: TicketData) -> str:
    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    old_ticket = new_sprint.get_ticket_by_id(id)
    if old_ticket is None:
        raise ValueError("Ticket not found.")

    idx = new_sprint.tickets.index(old_ticket)
    new_sprint.tickets[idx] = old_ticket.model_copy(update=ticket.model_dump())
    del old_ticket

    return f"Ticket updated.\n\n{show_sprint_plan()}"


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Move a tickets position (1 based) in the current sprint.")
def move_ticket(id: int, new_position: int) -> str:
    if new_position < 1:
        raise ValueError("Invalid position.")

    global new_sprint
    validate_sprint(sprint=new_sprint)

    # Update object
    ticket = new_sprint.get_ticket_by_id(id)
    if ticket is None:
        raise ValueError("Ticket not found.")

    new_sprint.tickets.remove(ticket)
    new_sprint.tickets.insert(new_position - 1, ticket)

    return f"Ticket moved.\n\n{show_sprint_plan()}"


approval_requested = False


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Submit the final sprint plan for approval by the user.")
def submit_sprint_plan() -> str:
    global new_sprint, approval_requested
    validate_sprint(sprint=new_sprint)
    if not new_sprint.tickets:
        raise ValueError("No tickets added to the sprint plan.")

    approval_requested = True

    print(
        f"""\
USER APPROVAL REQUESTED
-----------------------
{show_sprint_plan()}"""
    )

    return "Sprint plan submitted for approval."


@planning_proxy.register_for_execution()
@planner.register_for_llm(description="Abort the current sprint planning, removing all tickets.")
def abort_sprint_plan() -> str:
    global new_sprint, approval_requested
    new_sprint = None
    approval_requested = True

    print("USER APPROVAL REQUESTED\nSprint plan aborted.")

    return "Sprint plan aborted."


### Group Chat ###

user = UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    code_execution_config=False,
)


review_requested = False


def speaker_selection(last_speaker: Agent, groupchat: GroupChat) -> Agent | None:
    global approval_requested, review_requested
    if review_requested:
        return user

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
    global new_sprint, review_requested
    # Reset result object
    new_sprint = None
    review_requested = False

    if iteration > 0:
        # Review Previous Sprint
        review_requested = True
        chat_manager.initiate_chat(
            recipient=user,
            clear_history=False,
            message="Before starting the next sprint planning, provide a detailed review of the previous sprint.",
        )
        review_requested = False

    # Plan Sprint
    chat_manager.initiate_chat(
        recipient=planner,
        clear_history=False,
        max_turns=100,
        message=f"Start planning sprint {iteration}. If you are happy with the sprint plan, get the user's approval.",
    )

    # Retrieve result object
    return new_sprint
