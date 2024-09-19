import asyncio
import traceback
from textwrap import dedent

import client_request
from agency.coding import init_coder
from agency.lpu.standard import base_config
from agency.mangement import init_planner
from agency.tools.utils import generate_langchain_tool_schema
from autogen import Agent, ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from implementation import init_developers, run_implementation
from langchain.tools import BaseTool
from sprint_planning import init_planners, plan_sprint
from state import reset
from state.project_state import ProjectState
from state.sprint import Sprint, SprintResult, TicketStatus


async def main():
    # repo = state.reset(client_request=client_request.SMALL)
    reset()

    request = client_request.SMALL
    init_planners(request=request)
    init_developers(request=request)

    for i in range(5):
        sprint = plan_sprint(iteration=i)
        if sprint is None:
            # Project finished
            break

        run_implementation(sprint=sprint)

        print(f"""\
Sprint {i} finished.

{sprint.model_dump_json(indent=2)}""")

    # user = UserProxyAgent(
    #     name="User",
    #     human_input_mode="NEVER",
    #     code_execution_config=False,
    #     default_auto_reply="Keep going until you reach the goal.",
    # )

    # project_state = ProjectState(client_request=client_request.SMALL)

    # sprint_plan_proxy = init_planner(state=project_state)
    # coding_proxy = init_coder(state=project_state)

    # def speaker_selection_method(last_speaker: Agent, groupchat: GroupChat) -> Agent | None:
    #     if project_state.finished:
    #         return None

    #     if project_state.current_sprint is None:
    #         return sprint_plan_proxy

    #     return coding_proxy

    # group_chat = GroupChat(
    #     agents=[user, sprint_plan_proxy, coding_proxy],
    #     messages=[],
    #     speaker_selection_method=speaker_selection_method,
    # )
    # chat_manager = GroupChatManager(groupchat=group_chat)

    # user.initiate_chat(
    #     recipient=chat_manager,
    #     message="Start the project.",
    # )

    # def commit_callback(_):
    #     repo.index.add(["."])
    #     repo.index.commit("Commit changes.")

    # coding_task.callback = commit_callback
    # software_architect.tools.append(ShowDiff(repo=repo))

    # ### Kickoff + Project Setup ###
    # # How to get the project started? (Requirements? Architecture?) -> Question for before development
    # # Result: Sprint
    # output = kickoff_crew.kickoff(
    #     inputs={"client_request": client_request.SMALL, "code_structure": ShowDirTree()._run(path=None)}
    # )
    # sprint: Sprint | None = output.pydantic
    # sprint_history: list[SprintResult] = []

    # ### Sprint Loop ###
    # while True:
    #     # Step 1: Sprint Planning -> Skip in kickoff
    #     # What has to be done to bring the project closer to the goal? (Milestone?)
    #     # Result: Sprint
    #     if sprint is None:
    #         print("Starting Sprint Planning...")

    #         history_json = json.dumps([result.model_dump() for result in sprint_history], indent=4)
    #         output = sprint_planning_crew.kickoff(inputs={"sprint_history": history_json})
    #         sprint = output.pydantic

    #     # Step 2: Sprint Execution
    #     ### Dev Loop ###
    #     while sprint.open_tickets:
    #         # Step 2.1: Ticket Selection
    #         # What is the next logical ticket to work on?
    #         # Result: Ticket or TicketID
    #         ticket = sprint.open_tickets[0]

    #         # Step 2.2: Ticket Execution + Review
    #         # Did the ticket meet the acceptance criteria?
    #         # Result: Review or Rejection
    #         # ? Create Branch for Ticket
    #         if repo.active_branch != main_branch:
    #             raise Exception("Cannot start ticket while ticket branch is active.")

    #         ticket_branch = repo.create_head(f"{settings.ticket_prefix}{ticket.id}")
    #         ticket_branch.checkout()

    #         ticket_json = ticket.model_dump_json(indent=4)
    #         ticket_review = "You didn't start the ticket yet. A review will be available after you finish the ticket."
    #         while ticket.status != TicketStatus.DONE:
    #             ticket_review = dev_crew.kickoff(
    #                 inputs={
    #                     "ticket": ticket_json,
    #                     "ticket_review": ticket_review,
    #                     "code_structure": ShowDirTree()._run(path=None),
    #                 }
    #             ).raw
    #             if "APPROVED" in output:
    #                 # Finish the ticket -> removes it from the sprint
    #                 ticket.status = TicketStatus.DONE
    #                 break

    #         # ? Merge Ticket Branch
    #         main_branch.checkout()
    #         base = repo.merge_base(main_branch, ticket_branch)
    #         repo.index.merge_tree(ticket_branch, base=base)
    #         repo.index.commit(f"Merge branch '{ticket_branch.name}' into {main_branch.name}")

    #         # ? Delete Ticket Branch
    #         repo.delete_head(ticket_branch)

    #     # Step 3: Sprint Retrospective
    #     # Was the sprint successful? What can be improved?
    #     # Result: SprintResult
    #     output = sprint_review_crew.kickoff(
    #         inputs={
    #             "sprint": sprint.model_dump_json(indent=4),
    #             "sprint_history": history_json,
    #         }
    #     )
    #     sprint_result: SprintResult = output.pydantic
    #     sprint_history.append(sprint_result)
    #     sprint = None

    #     # Step 4: Evaluation
    #     # Is the project finished?
    #     # Result: Iteration or Break
    #     if sprint_result.project_finished:
    #         break

    print("Project finished.")


if __name__ == "__main__":
    while True:
        try:
            prompt = input("Press Enter to start the conversation... [exit to quit]\n")
            if prompt == "exit":
                break

            asyncio.run(main())
            print("Conversation finished.")

        except Exception as e:
            print(traceback.format_exc())
