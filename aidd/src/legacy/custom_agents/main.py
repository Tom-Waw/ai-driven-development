import json
import traceback

import openai
import ram
from lpu.agent import Agent
from prompts.chains.project_kickoff import get_example_project, run_kickoff_chain
from prompts.chains.sprint_planning import get_example_sprint, run_spint_planning_chain
from prompts.template import Template
from pydantic import BaseModel
from tools import editor

client_request = """
Create a local mini game in the terminal that allows the user to create a character.
The user can give it a name and choose a character type.
There are three character  types: warrior, mage, and rogue.
One can pick the character type and the character will have different stats based on the type.
Also each character type has unique weapons and armor to choose from.

Also the user should be able to save the character to a file and load it later or delete it.
"""


def main():
    # project = run_kickoff_chain(client_request)
    project = get_example_project()

    # sprint = run_spint_planning_chain(project=project)
    sprint = get_example_sprint()

    sw_engineer = Agent(
        "Software Engineer",
        system_message=f"""
You are a software engineer working on a scrum project.
The manager has given you the following project to work on:
{project.model_dump_json(indent=4)}

You are supervising the development of the project.
You will be working with a team of developers to complete the project.
The project is implemented in python.

The project has been broken down into sprints.
You are currently working on sprint number 1 with the following goal:
{sprint.goal}

You will be given tickets one by one.
Your job is to layout a solution strategy for the ticket the developers can follow.
""",
    )

    dev = Agent(
        "Developer",
        system_message=f"""
You are a software developer working on a new feature.
You are especially profounded in python.
You are working in a sprint to develop a new feature.

You will receive tickets to work on one by one.
With the help of the software engineer, you will work through his solution strategy to complete the ticket.
""",
        tools=editor.tools,
    )
    SUBMIT = "SUBMIT"
    for ticket in sprint.tickets:
        dev.reset()

        ticket_json = ticket.model_dump_json(indent=4)
        project_structure = editor.ShowDirTree().call()

        class SolutionStep(BaseModel):
            description: str

        class SolutionStrategy(BaseModel):
            steps: list[SolutionStep]

        response = sw_engineer.prompt(
            f"""
The next ticket for the developers is:
{ticket_json}

The current state of the project is as follows:
{project_structure}

Please layout a solution strategy for the developers to follow.
The developers will follow exactly the steps you provide.
Be as fine-grained as possible. Include implementation hints where necessary.
                """,
            response_format=SolutionStrategy,
        )
        solution_strategy: SolutionStrategy = response.parsed

        response = dev.prompt(
            f"""
The next ticket you are working on is:
{ticket_json}

Follow the solution strategy provided by the software engineer:
{solution_strategy.model_dump_json(indent=4)}

The current state of the project is as follows:
{project_structure}

In an iterative process, work on the ticket and complete the task.
When you are confident that the ticket is completed, submit your work for review and validation by the product manager.
Submit by replying with '{SUBMIT}'.
    """
        )

        while True:
            if response.refusal or (response.content and SUBMIT in response.content):
                break

            response = dev.prompt(None)

    print("Sprint completed!")


if __name__ == "__main__":
    while True:
        try:
            ram.reset()
            prompt = input("Press Enter to start the conversation... [exit to quit]\n")
            if prompt == "exit":
                break

            main()
        except Exception as e:
            print(traceback.format_exc())
