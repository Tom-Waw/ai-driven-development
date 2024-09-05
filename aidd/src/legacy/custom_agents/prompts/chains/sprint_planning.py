from lpu.agent import Agent
from prompts.template import Template
from ram.project import Project
from ram.ticket_system import Sprint


def run_spint_planning_chain(project: Project) -> Sprint:
    agent = Agent(
        "Product Manager",
        system_message="You are the product manager for a new project.",
    )

    sprint = agent.prompt(
        Template(
            """
Given the <project_description> and <requirements> below, you have to plan the first sprint for the project.
All tickets have to aim to acchieve the goal of the sprint.
The tickets should be small and focused on a single task, to be easily tracked and validated for completion.

This is the very first sprint of the project. The project directory is currently empty and you have to start from scratch.

<project_description>
{{description}}
</project_description>

<requirements>
{{requirements}}
</requirements>
"""
        ).render(input=project),
        response_format=Sprint,
    )

    return sprint.parsed


def get_example_sprint() -> Sprint:
    return Sprint.model_validate_json(
        """
{
    "goal": "Establish the foundational elements of the character creation mini game.",
    "tickets": [
        {
            "id": 1,
            "expectation": "Create a basic project structure for the mini game.",
            "acceptance_criteria": "Project directory is created with subdirectories for assets, scripts, and styles.",
            "description": "Set up the initial project structure including folders for assets (images, sounds), scripts (JavaScript or Python files), and styles (CSS files).",
            "title": "Setup Project Structure",
            "status": "todo"
        },
        {
            "id": 2,
            "expectation": "Implement a basic UI layout for character creation.",
            "acceptance_criteria": "A simple UI is displayed with sections for character type selection, appearance customization, and name input.",
            "description": "Design and implement a basic user interface that includes dropdowns or buttons for selecting character types and input fields for customizing appearance and entering a name.",
            "title": "Create Basic UI Layout",
            "status": "todo"
        },
        {
            "id": 3,
            "expectation": "Develop functionality to select character types.",
            "acceptance_criteria": "User can select from warrior, mage, and rogue character types, and the selection is reflected in the UI.",
            "description": "Implement the logic to allow users to select a character type (warrior, mage, rogue) and display the selected type in the UI.",
            "title": "Character Type Selection",
            "status": "todo"
        },
        {
            "id": 4,
            "expectation": "Create a character customization feature.",
            "acceptance_criteria": "User can customize character appearance (e.g., color, features) and the changes are visually represented in the UI.",
            "description": "Develop the functionality that allows users to customize their character's appearance, including options for colors and features, and ensure these changes are reflected in the UI.",
            "title": "Character Customization Feature",
            "status": "todo"
        },
        {
            "id": 5,
            "expectation": "Implement character naming functionality.",
            "acceptance_criteria": "User can input a name for the character and it is displayed in the UI.",
            "description": "Create an input field for users to enter a character name and ensure that the name is displayed correctly in the character profile.",
            "title": "Character Naming Functionality",
            "status": "todo"
        },
        {
            "id": 6,
            "expectation": "Define character stats based on type.",
            "acceptance_criteria": "Each character type has distinct stats that are displayed when selected.",
            "description": "Establish the stats for each character type (warrior, mage, rogue) and ensure these stats are displayed in the UI when a type is selected.",
            "title": "Define Character Stats",
            "status": "todo"
        },
        {
            "id": 7,
            "expectation": "Create functionality to save character data to a file.",
            "acceptance_criteria": "User can save character data to a local file successfully.",
            "description": "Implement the logic to save the character's name, type, appearance, and stats to a local file in a structured format (e.g., JSON).",
            "title": "Save Character Data",
            "status": "todo"
        },
        {
            "id": 8,
            "expectation": "Create functionality to load character data from a file.",
            "acceptance_criteria": "User can load previously saved character data and it is displayed in the UI.",
            "description": "Develop the functionality to read character data from a local file and populate the UI with the loaded character's information.",
            "title": "Load Character Data",
            "status": "todo"
        },
        {
            "id": 9,
            "expectation": "Implement character deletion functionality.",
            "acceptance_criteria": "User can delete a character profile and confirm the deletion in the UI.",
            "description": "Create the logic that allows users to delete a character profile and ensure that the UI reflects this change appropriately.",
            "title": "Delete Character Profile",
            "status": "todo"
        }
    ]
}"""
    )
