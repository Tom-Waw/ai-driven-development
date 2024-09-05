import traceback

import client_request
import openai
import ram
from autogen import GroupChat, GroupChatManager, UserProxyAgent
from lpu.standard import MODEL, TERMINATION_SYMBOL, base_config
from ram import editor, ticket_system
from ram.ticket_system import Sprint
from aidd.src.lpu.agents import developer, project_manager, software_engineer
from tools.editor.tools import show_dir_tree


def main():
    ram.reset()

    thoughts = UserProxyAgent(
        name="Thoughts",
        system_message="This is an internal monologue. You can think of it as a conversation with yourself.",
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    ### ! Kickoff ###

    result = thoughts.initiate_chat(
        recipient=project_manager,
        max_turns=1,
        message=f"""
The client has requested a software application (see <client_request>).
Create a briefing for your development team. The briefing should include the client request and the project goal/scope.
Be precise and clear in your communication. Do not provide more information than necessary.

<client_request>
{client_request.SMALL}
</client_request>""",
    )
    briefing = result.summary

    for agent in [software_engineer, developer]:
        agent.update_system_message(
            f"""{agent.system_message}
The project manager has provided you with a briefing for the project.
{briefing}"""
        )

    finished = False
    while not finished:
        ### ! Sprint Planning ###

        result = thoughts.initiate_chat(
            recipient=project_manager,
            max_turns=1,
            message=f"""
Read the project briefing and start planning the application.
Based on the current <state> of the project and <former_sprints>, define a sprint goal and create tickets for the developers.

<state>
{show_dir_tree()}
</state>

<former_sprints>
{ticket_system.model_dump_json(indent=4, include="former_sprints")}
</former_sprints>""",
        )
        client = openai.OpenAI()
        result = client.beta.chat.completions.parse(
            model=MODEL,
            messages=result.chat_history,
            response_format=Sprint,
        )
        sprint_planning = result.choices[0].message.parsed
        if sprint_planning is None:
            raise ValueError("Sprint planning is required.")

        ### ! Development Loop ###
        for ticket in sprint_planning.tickets:

            thoughts.initiate_chat(
                recipient=developer,
                max_turns=1,
                message=f"""
Read the <ticket> and start developing the feature.
Use the provided tools and resources to complete the task.
If you think you are finished, submit the code by terminating the conversation.
Only submit the code if you are confident in your work.

<ticket>
{ticket.model_dump_json(indent=4)}
</ticket>""",
            )

            ### ! Review  Step ###

            thoughts.initiate_chat(
                recipient=software_engineer,
                max_turns=1,
                message=f"""
Read the <ticket> submitted by the developer.
Review the <changes> made in the code and provide feedback.
If the code meets the requirements, approve the ticket.
If the code does not meet the requirements, provide feedback to the developer.

<ticket>
{ticket.model_dump_json(indent=4)}
</ticket>

<changes>
{ticket.changes}
</changes>""",
            )

        ### ! Retrospective ###

        result = thoughts.initiate_chat(
            recipient=project_manager,
            max_turns=1,
            message=f"""
The sprint has ended. Conduct a retrospective meeting with your team.
Discuss the sprint goal, the progress made, and the challenges faced.
Identify areas for improvement and create action items for the next sprint.
            """,
        )
        retrospective = result.summary

        finished = True

    print("Conversation ended.")


# def get_planning_group(briefing: str) -> GroupChat:


if __name__ == "__main__":
    while True:
        try:
            prompt = input("Press Enter to start the conversation... [exit to quit]\n")
            if prompt == "exit":
                break

            main()
        except Exception as e:
            print(traceback.format_exc())
