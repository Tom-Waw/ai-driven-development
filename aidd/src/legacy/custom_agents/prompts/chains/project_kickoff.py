from lpu.agent import Agent
from prompts.template import Template
from ram.project import Project, Requirements


def run_kickoff_chain(project_description: str) -> Project:
    agent = Agent(
        "Requirements Engineer",
        system_message="""
You are a Requirements Engineer tasked with gathering and analyzing the requirements for a new project.
""",
    )

    # Requirements
    RequirementsTemplate = Template(
        """
Given the <project_description> from a clients request, extract the requirements and constraints from the description.
"""
        + """
Collect information fitting the following categories:
1. Project Objective and Scope
    - Purpose: Understand the primary goals and what the client hopes to achieve with the application.
    - Necessity: Helps in defining the project's boundaries and ensures that all features align with the overarching business goals.
2. Functional Requirements
    - Specific Functions: Detailed descriptions of all required functionalities, such as user interactions, data processing, and expected outputs.
    - Necessity: These are essential for developers to understand what features need to be built and how they should perform.
3. Non-Functional Requirements
    - Performance: Speed, responsiveness, scalability, and other performance metrics.
    - Security: Data integrity, confidentiality measures, and compliance requirements.
    - Necessity: Non-functional requirements ensure the application is reliable, secure, and capable of operating under defined constraints.
4. Technical Requirements
    - Technology Stack: Specific platforms, languages, and frameworks the client prefers or requires.
    - Integration Needs: Details on external systems or services the application must integrate with.
    - Necessity: These requirements help in choosing the right tools and strategies for development and ensuring compatibility with existing systems.

<project_description>
{{description}}
</project_description>
    """
    )
    requirements = agent.prompt(
        RequirementsTemplate.render(description=project_description),
        response_format=Requirements,
    )

    return Project(
        description=project_description,
        requirements=requirements.parsed,
    )


def get_example_project() -> Project:
    return Project.model_validate_json(
        """
{
    "description": "\\nCreate a mini game that allows the user to create a character.\\nThe user can change the appearance of the character and give it a name.\\nThere are three character  types: warrior, mage, and rogue.\\nOne can pick the character type and the character will have different stats based on the type.\\nAlso each character type has unique weapons and armor to choose from.\\n\\nThe game should have a simple UI that allows the user to interact with the game.\\nAlso the user should be able to save the character to a file and load it later or delete it.\\n",
    "requirements": {
        "objectives": [
            "Create a mini game that allows users to create and customize characters.",
            "Enable users to choose from three character types: warrior, mage, and rogue.",
            "Provide functionality for users to save, load, and delete character profiles."
        ],
        "functional_requirements": [
            "User can create a character by selecting a type and customizing its appearance.",
            "User can assign a name to the character.",
            "Character types (warrior, mage, rogue) have distinct stats and unique weapons and armor.",
            "User interface must allow for easy interaction and navigation.",
            "User must be able to save character data to a file.",
            "User must be able to load previously saved character data.",
            "User must be able to delete character profiles."
        ],
        "non_functional_requirements": [
            "The game should have a responsive UI that loads quickly and is easy to navigate.",
            "The application should ensure data integrity when saving and loading character files.",
            "The application should be secure, preventing unauthorized access to saved character data."
        ],
        "technical_requirements": [
            "The game should be developed using a suitable programming language (e.g., JavaScript, Python).",
            "The UI should be built using a framework that supports interactive elements (e.g., React, Unity).",
            "The application must be able to read from and write to local files for saving and loading character data."
        ]
    }
}
"""
    )
