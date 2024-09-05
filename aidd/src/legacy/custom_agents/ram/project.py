from pydantic import BaseModel


class Requirements(BaseModel):
    objectives: list[str]
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    technical_requirements: list[str]


class Project(BaseModel):
    description: str
    requirements: Requirements
