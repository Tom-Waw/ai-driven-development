import asyncio
import traceback

import client_request
from crew.development import dev_crew
from crew.management import kickoff_crew, sprint_planning_crew
from state.project_state import ProjectState
from state.sprint import Sprint, TicketStatus


async def main():
    kickoff_inputs = {"client_request": client_request.SMALL}
    # await pipeline.process_single_kickoff(kickoff_input=kickoff_inputs)

    output = kickoff_crew.kickoff(inputs=kickoff_inputs)
    project_state: ProjectState = output.pydantic

    finished = False
    while not finished:
        output = sprint_planning_crew.kickoff(
            inputs={"insights": project_state.model_dump_json(indent=4, exclude="current_sprint")}
        )
        sprint: Sprint = output.pydantic

        while sprint.open_tickets:
            ticket = sprint.open_tickets[0]

            while not ticket.status == TicketStatus.DONE:
                dev_inputs = {
                    "project_info": project_state.model_dump_json(
                        indent=4, include=("client_request", "goal", "requirements")
                    ),
                    "ticket": ticket.model_dump_json(indent=4),
                }
                dev_crew.kickoff(inputs=dev_inputs)

                break

            break

        break

    print("Resulting project state:")
    print(project_state.model_dump_json(indent=4))


while True:
    try:
        prompt = input("Press Enter to start the conversation... [exit to quit]\n")
        if prompt == "exit":
            break

        asyncio.run(main())

    except Exception as e:
        print(traceback.format_exc())
