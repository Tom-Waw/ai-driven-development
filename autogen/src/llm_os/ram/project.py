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
