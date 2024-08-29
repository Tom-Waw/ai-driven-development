from lpu.agent import Agent
from prompts.template import Template
from ram.project import Planning, Project, Requirements, SystemDesign


def run_planning_chain(project_description: str) -> Project:
    agent = Agent()

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

    # Milestones and Risks
    planning = agent.prompt(
        """
Given the requirements, create a project plan that outlines the milestones and risks associated with the project.
""",
        response_format=Planning,
    )

    # System Design
    # 1. Architecture Suggestions
    agent.prompt(
        """
Given the requirements and milestones, evaluate multiple possible system designs and describe the overall idea of each one.
Include the architectural principle, network design and data flow design.
"""
        + """
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
    )

    # 2. Design Selection
    system_design = agent.prompt(
        """
Given the requirements and milestones, choose a system architecture that best fits the project.
Outlines the components and relationships between them.
""",
        response_format=SystemDesign,
    )

    return Project(
        description=project_description,
        requirements=requirements.parsed,
        planning=planning.parsed,
        system_design=system_design.parsed,
    )
