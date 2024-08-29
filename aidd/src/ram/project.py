from pydantic import BaseModel

### Requirements ###


class Requirements(BaseModel):
    objectives: list[str]
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    technical_requirements: list[str]


### Planning ###


class Risk(BaseModel):
    description: str
    mitigation: str


class Milestone(BaseModel):
    name: str
    description: str
    acceptance_criteria: list[str]
    risks: list[Risk]


class Planning(BaseModel):
    milestones: list[Milestone]


### System Design ###


class ArchitectureComponent(BaseModel):
    name: str
    description: str


class Relationship(BaseModel):
    component1: str
    component2: str
    description: str


class Architecture(BaseModel):
    components: list[ArchitectureComponent]
    relationships: list[Relationship]


class SystemDesign(BaseModel):
    description: str
    architecture: Architecture


### Project ###


class Project(BaseModel):
    description: str
    requirements: Requirements
    planning: Planning
    system_design: SystemDesign


example_project = Project.model_validate_json(
    """
{
    "description": "Create a mini game that allows the user to create a character.\\nThe user can change the appearance of the character and give it a name.\\nThere are three character types: warrior, mage, and rogue.\\nOne can pick the character type and the character will have different stats based on the type.\\nAlso each character type has unique weapons and armor to choose from.\\n\\nThe game should have a simple UI that allows the user to interact with the game.\\nAlso the user should be able to save the character to a file and load it later or delete it.",
    "requirements": {
        "objectives": [
            "Develop a user-friendly application to streamline project management.",
            "Enhance collaboration among team members."
        ],
        "functional_requirements": [
            "User authentication and authorization.",
            "Task assignment and tracking.",
            "Real-time chat functionality.",
            "File sharing capabilities."
        ],
        "non_functional_requirements": [
            "Application must load within 2 seconds.",
            "Support for at least 100 concurrent users.",
            "Data encryption for user information.",
            "Compliance with GDPR regulations."
        ],
        "technical_requirements": [
            "Built using React for the frontend and Node.js for the backend.",
            "Integration with third-party APIs for notifications.",
            "Database must be PostgreSQL."
        ]
    },
    "planning": {
        "milestones": [
            {
                "name": "Project Kickoff",
                "description": "Initiate the project and gather detailed requirements.",
                "acceptance_criteria": [
                    "Requirements documented",
                    "Stakeholder approval obtained"
                ],
                "risks": [
                    {
                        "description": "Stakeholder misalignment on requirements",
                        "mitigation": "Conduct regular meetings to ensure alignment"
                    }
                ]
            },
            {
                "name": "Design Phase",
                "description": "Create wireframes and architecture for the application.",
                "acceptance_criteria": [
                    "Wireframes approved",
                    "Architecture documented"
                ],
                "risks": [
                    {
                        "description": "Design not meeting user expectations",
                        "mitigation": "Involve users in the design review process"
                    }
                ]
            },
            {
                "name": "Development Phase",
                "description": "Develop the application based on the approved designs.",
                "acceptance_criteria": [
                    "Core functionalities implemented",
                    "Code reviewed"
                ],
                "risks": [
                    {
                        "description": "Technical challenges with integration",
                        "mitigation": "Allocate time for research and prototyping"
                    },
                    {
                        "description": "Delays in development timeline",
                        "mitigation": "Implement agile methodologies for flexibility"
                    }
                ]
            },
            {
                "name": "Testing Phase",
                "description": "Conduct thorough testing of the application.",
                "acceptance_criteria": [
                    "All test cases passed",
                    "User acceptance testing completed"
                ],
                "risks": [
                    {
                        "description": "Undetected bugs in production",
                        "mitigation": "Implement automated testing and thorough QA processes"
                    }
                ]
            },
            {
                "name": "Deployment",
                "description": "Deploy the application to the production environment.",
                "acceptance_criteria": [
                    "Application live",
                    "User feedback collected"
                ],
                "risks": [
                    {
                        "description": "Downtime during deployment",
                        "mitigation": "Schedule deployment during off-peak hours"
                    }
                ]
            },
            {
                "name": "Post-Deployment Review",
                "description": "Review project outcomes and gather feedback for future improvements.",
                "acceptance_criteria": [
                    "Feedback documented",
                    "Lessons learned identified"
                ],
                "risks": [
                    {
                        "description": "Inadequate user adoption",
                        "mitigation": "Provide training and support for users"
                    }
                ]
            }
        ]
    },
    "system_design": {
        "description": "Microservices architecture to support a user-friendly project management application with real-time collaboration features.",
        "architecture": {
            "components": [
                {
                    "name": "Frontend Application",
                    "description": "Built using React, this component handles user interface and user interactions."
                },
                {
                    "name": "Authentication Service",
                    "description": "Handles user authentication and authorization, ensuring secure access to the application."
                },
                {
                    "name": "Task Management Service",
                    "description": "Manages task assignment, tracking, and updates for project management."
                },
                {
                    "name": "Chat Service",
                    "description": "Facilitates real-time chat functionality among team members."
                },
                {
                    "name": "File Storage Service",
                    "description": "Handles file sharing capabilities, allowing users to upload and share documents."
                },
                {
                    "name": "Notification Service",
                    "description": "Integrates with third-party APIs to send notifications to users."
                },
                {
                    "name": "Database",
                    "description": "PostgreSQL database for storing user data, tasks, and chat history."
                }
            ],
            "relationships": [
                {
                    "component1": "Frontend Application",
                    "component2": "Authentication Service",
                    "description": "The frontend communicates with the authentication service for user login and registration."
                },
                {
                    "component1": "Frontend Application",
                    "component2": "Task Management Service",
                    "description": "The frontend interacts with the task management service to display and update tasks."
                },
                {
                    "component1": "Frontend Application",
                    "component2": "Chat Service",
                    "description": "The frontend connects to the chat service for real-time messaging."
                },
                {
                    "component1": "Frontend Application",
                    "component2": "File Storage Service",
                    "description": "The frontend uses the file storage service to upload and retrieve files."
                },
                {
                    "component1": "Task Management Service",
                    "component2": "Database",
                    "description": "The task management service interacts with the database to store and retrieve task data."
                },
                {
                    "component1": "Chat Service",
                    "component2": "Database",
                    "description": "The chat service stores chat messages in the database."
                },
                {
                    "component1": "Notification Service",
                    "component2": "Frontend Application",
                    "description": "The notification service sends updates to the frontend for user notifications."
                }
            ]
        }
    }
}
"""
)
