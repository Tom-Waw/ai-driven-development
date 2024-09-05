from agents import create_assistant
from llm_os.lpu.standard import is_termination_message
from llm_os.ram.project import Planning, Project, Requirements, SystemDesign
from prompts.abc import Template

from autogen import UserProxyAgent


class RequirementsTemplate(Template):
    template = """
Given the <project_description> from a clients request, extract the requirements and constraints from the description.
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

Respond in JSON format, no extra description is needed.

<example>
{
    "objectives": [
        "objective1",
        "objective2"
    ],
    "functional_requirements": [
        "functional_requirement1",
        "functional_requirement2",
        "functional_requirement3"
    ],
    "non_functional_requirements": [
        "non_functional_requirement1",
        "non_functional_requirement2"
    ],
    "technical_requirements": [
        "technical_requirement1"
    ]
}
</example>
"""

    @classmethod
    def render(cls, description: str):
        return super().render(description=description)


PlanningPrompt = """
Given the <requirements>, create a project plan that outlines the milestones and risks associated with the project.
Respond in JSON format, no extra description is needed.

<example>
{
    milestones: [
        {
            name: "Milestone 1",
            description: "Description of the milestone",
            acceptance_criteria: ["Criteria 1", "Criteria 2"],
            risks: [
                {
                    description: "Description of the risk",
                    mitigation: "Mitigation strategy"
                }
            ]
        },
        {
            name: "Milestone 2",
            description: "Description of the milestone",
            acceptance_criteria: ["Criteria 1", "Criteria 2"],
            risks: [
                {
                    description: "Description of the risk",
                    mitigation: "Mitigation strategy"
                },
                {
                    description: "Description of the risk",
                    mitigation: "Mitigation strategy"
                }
            ]
        }
    ],
}
</example>
"""

EvaluationPrompt = """
Given the <requirements> and <planning>, evaluate multiple possible system designs and describe the overall idea of each one.
Include the architectural principle, network design and data flow design.

<example>
## System Design 1 Name

### Description
Description of the system design / architecture

### Network Design
Description of the network design

### Data Flow Design
Description of the data flow design

## System Design 2 Name
...
</example>
"""

SystemDesignPrompt = """
Given the <requirements> and <planning>, choose a system architecture that best fits the project.
Outlines the components and relationships between them.
Respond in JSON format, no extra description is needed.

<example>
{
    description: "Copy of the description of the system design you chose",
    architecture: {
        components: [
            {
                name: "Component 1",
                description: "Description of the component"
            },
            {
                name: "Component 2",
                description: "Description of the component"
            },
            {
                name: "Component 3",
                description: "Description of the component"
            }
        ],
        relationships: [
            {
                component1: "Component 1",
                component2: "Component 2",
                description: "Description of the relationship"
            },
            {
                component1: "Component 3",
                component2: "Component 1",
                description: "Description of the relationship"
            }
        ]
    }
}
</example>
"""


def run_project_planning_chain(project_description: str) -> Project:
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
        code_execution_config=False,
    )
    assistant = create_assistant()

    results = user.initiate_chats(
        chat_queue=[
            {
                "recipient": assistant,
                "message": RequirementsTemplate.render(description=project_description),
                "max_turns": 1,
            },
            {
                "recipient": assistant,
                "message": PlanningPrompt,
                "max_turns": 1,
                "carryover": "requirements:",
            },
            {
                "recipient": assistant,
                "message": EvaluationPrompt,
                "max_turns": 1,
                "carryover": "requirements and planning:",
            },
            {
                "recipient": assistant,
                "message": SystemDesignPrompt,
                "max_turns": 1,
                "carryover": "requirements and planning:",
                "finished_chat_indexes_to_exclude_from_carryover": [2],
            },
        ]
    )

    requirements = Requirements.model_validate_json(results[0].summary)
    planning = Planning.model_validate_json(results[1].summary)
    system_design = SystemDesign.model_validate_json(results[3].summary)

    return Project(
        description=project_description,
        requirements=requirements,
        planning=planning,
        system_design=system_design,
    )
