import sys

sys.dont_write_bytecode = True

import asyncio
import json
import traceback
from textwrap import dedent

import client_request

# from agency.agents import coder, software_architect
from agency.lpu.standard import base_config
from agency.tools import editor
from agency.tools.editor import (
    CLICommand,
    CreateDir,
    CreateFile,
    DeletePath,
    ListDir,
    MovePath,
    ReadFile,
    RunCode,
    ShowDirTree,
    WriteContent,
)
from agency.tools.utils import register_langchain_tool
from autogen import AssistantAgent, UserProxyAgent
from langchain.tools import BaseTool
from settings import settings
from state import reset
from state.sprint import Sprint, SprintResult, TicketStatus


async def main():
    # repo = state.reset(client_request=client_request.SMALL)
    repo = reset()
    main_branch = repo.active_branch
    repo.index.add(["."])
    repo.index.commit("Commit changes.")

    coder = AssistantAgent(
        name="Coder",
        system_message=f"""\
You are a coder, equipped with the knowledge and the tools to write quality code.
Given a Ticket, you can find the best way to implement the requested feature in the code base.

Code Conventions
-----------------
{ReadFile()._run("docs/CONVENTIONS.md")}
        """,
        llm_config=base_config,
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        default_auto_reply="Keep going until you reach the goal.",
    )

    tools: list[BaseTool] = [
        CreateDir(),
        CreateFile(),
        ListDir(),
        ShowDirTree(),
        ReadFile(),
        WriteContent(),
        MovePath(),
        DeletePath(),
        CLICommand(),
        RunCode(),
    ]

    for tool in tools:
        register_langchain_tool(tool, caller=coder, executor=user)

    user.initiate_chat(
        recipient=coder,
        # max_turns=1,
        message=dedent(
            f"""\
Start implementing a prototype of a snake game with a simple GUI in python (pygame).
First plan the structure of the project and dokument it in the SW_DESIGN.md file.
After that, start implementing the game.
You can make general assumptions about the game, but don't go too far.

I will not answer any questions about the game, you have to figure it out yourself.
Write and run tests to confirm the functionality of the game.

If you are satisfied with the result, you can finish the project by replying with 'TERMINATE'.

Working directory contents
--------------------------
{editor.ShowDirTree()._run(None)}
            """
        ),
    )

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


while True:
    try:
        prompt = input("Press Enter to start the conversation... [exit to quit]\n")
        if prompt == "exit":
            break

        asyncio.run(main())
        print("Conversation finished.")

    except Exception as e:
        print(traceback.format_exc())
