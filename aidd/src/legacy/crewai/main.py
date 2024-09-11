import asyncio
import json
import traceback
from textwrap import dedent

import client_request
from agency.agents import coder, software_architect
from agency.tools.editor import ShowDirTree
from agency.tools.management import ShowDiff
from crewai import Crew, Task
from settings import settings
from state import reset
from state.sprint import Sprint, SprintResult, TicketStatus

### Crews ###

kickoff_crew = Crew(
    agents=[
        software_architect,
    ],
    tasks=[
        Task(
            agent=software_architect.copy(),
            description=dedent(
                """\
                Welcome to the project! Let's get started.
                The project has been initiated with the following client request:
                {client_request}

                You will not get any more information than this from the client.
                You can make general assumptions about the project based on the client request.
                The project will be developed locally. The repository is initialized and ready to be used.

                Current Repository Snapshot
                ---------------------------
                {code_structure}

                To get the project rolling, create the first sprint plan with tickets to setup and initiate an MVP to build upon.
                The first sprint should be focused on architectural decisions.
                After the first sprint the project should be in perfect shape to start implementing the features in detail.
                """
            ),
            expected_output="The first sprint plan with tickets to create an MVP to build upon.",
            output_pydantic=Sprint,
        )
    ],
    planning=True,
    verbose=True,
)

sprint_planning_crew = Crew(
    agents=[
        software_architect.copy(),
    ],
    tasks=[
        Task(
            agent=software_architect,
            description=dedent(
                """\
                Given the results of former sprints, plan the next sprint.
                Think about the next goal your team needs to achieve.
                With that goal in mind, create tickets for the developers to accomplish said goal.
                After completing this task, the sprint will automatically start.

                History
                -------
                {sprint_history}
                """
            ),
            expected_output="A sprint plan with tickets for the developers to work on.",
            output_pydantic=Sprint,
        ),
    ],
    planning=True,
    verbose=True,
)


dev_crew = Crew(
    agents=[
        software_architect.copy(),
        coder.copy(),
    ],
    tasks=[
        (
            coding_task := Task(
                agent=coder,
                description=dedent(
                    """\
                You received a new ticket or a ticket review.
                Start working on the ticket to implement the required changes.
                Use the provided tools to persist the code changes in the project repository.
                Only finish this task when the ticket is completed and the code is ready for review.

                Ticket
                ------
                {ticket}

                Review
                ------
                {ticket_review}

                Current Repository Content
                --------------------------
                {code_structure}
                """
                ),
                expected_output="The confirmation of the ticket completion.",
            )
        ),
        Task(
            agent=software_architect,
            description=dedent(
                """\
                The developer has finished the ticket. Review the code changes and provide feedback.
                Only if you have no further improvements or comments, the ticket will be approved and marked as done.

                Ticket
                ------
                {ticket}
                """
            ),
            expected_output="A detailed review of the missing or improvable changes. Reply 'APPROVED' to indicate that the ticket is finally done.",
        ),
    ],
    planning=True,
    verbose=True,
)

sprint_review_crew = Crew(
    agents=[
        software_architect.copy(),
        coder.copy(),
    ],
    tasks=[
        Task(
            agent=software_architect,
            description=dedent(
                """\
                The sprint has been completed. Review the sprint and provide feedback.
                Think about what went well and what could be improved.
                Based on your insights, decide whether the project is finished or if another sprint is needed.

                Sprint
                ------
                {sprint}

                History
                -------
                {sprint_history}
                """
            ),
            expected_output="The result of the sprint review.",
            output_pydantic=SprintResult,
        ),
    ],
    planning=True,
    verbose=True,
)


### Process ###


async def main():
    # repo = state.reset(client_request=client_request.SMALL)
    repo = reset()
    main_branch = repo.active_branch
    repo.index.add(["."])
    repo.index.commit("Commit changes.")

    def commit_callback(_):
        repo.index.add(["."])
        repo.index.commit("Commit changes.")

    coding_task.callback = commit_callback
    software_architect.tools.append(ShowDiff(repo=repo))

    ### Kickoff + Project Setup ###
    # How to get the project started? (Requirements? Architecture?) -> Question for before development
    # Result: Sprint
    output = kickoff_crew.kickoff(
        inputs={"client_request": client_request.SMALL, "code_structure": ShowDirTree()._run(path=None)}
    )
    sprint: Sprint | None = output.pydantic
    sprint_history: list[SprintResult] = []

    ### Sprint Loop ###
    while True:
        # Step 1: Sprint Planning -> Skip in kickoff
        # What has to be done to bring the project closer to the goal? (Milestone?)
        # Result: Sprint
        if sprint is None:
            print("Starting Sprint Planning...")

            history_json = json.dumps([result.model_dump() for result in sprint_history], indent=4)
            output = sprint_planning_crew.kickoff(inputs={"sprint_history": history_json})
            sprint = output.pydantic

        # Step 2: Sprint Execution
        ### Dev Loop ###
        while sprint.open_tickets:
            # Step 2.1: Ticket Selection
            # What is the next logical ticket to work on?
            # Result: Ticket or TicketID
            ticket = sprint.open_tickets[0]

            # Step 2.2: Ticket Execution + Review
            # Did the ticket meet the acceptance criteria?
            # Result: Review or Rejection
            # ? Create Branch for Ticket
            if repo.active_branch != main_branch:
                raise Exception("Cannot start ticket while ticket branch is active.")

            ticket_branch = repo.create_head(f"{settings.ticket_prefix}{ticket.id}")
            ticket_branch.checkout()

            ticket_json = ticket.model_dump_json(indent=4)
            ticket_review = "You didn't start the ticket yet. A review will be available after you finish the ticket."
            while ticket.status != TicketStatus.DONE:
                ticket_review = dev_crew.kickoff(
                    inputs={
                        "ticket": ticket_json,
                        "ticket_review": ticket_review,
                        "code_structure": ShowDirTree()._run(path=None),
                    }
                ).raw
                if "APPROVED" in output:
                    # Finish the ticket -> removes it from the sprint
                    ticket.status = TicketStatus.DONE
                    break

            # ? Merge Ticket Branch
            main_branch.checkout()
            base = repo.merge_base(main_branch, ticket_branch)
            repo.index.merge_tree(ticket_branch, base=base)
            repo.index.commit(f"Merge branch '{ticket_branch.name}' into {main_branch.name}")

            # ? Delete Ticket Branch
            repo.delete_head(ticket_branch)

        # Step 3: Sprint Retrospective
        # Was the sprint successful? What can be improved?
        # Result: SprintResult
        output = sprint_review_crew.kickoff(
            inputs={
                "sprint": sprint.model_dump_json(indent=4),
                "sprint_history": history_json,
            }
        )
        sprint_result: SprintResult = output.pydantic
        sprint_history.append(sprint_result)
        sprint = None

        # Step 4: Evaluation
        # Is the project finished?
        # Result: Iteration or Break
        if sprint_result.project_finished:
            break

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
