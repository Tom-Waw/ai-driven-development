from pydantic import BaseModel, Field
from state.sprint import Sprint, SprintResult


class ProjectStateInit(BaseModel):
    client_request: str = Field(..., description="The client request that initiated the project.")
    goal: str = Field(..., description="The goal of the project.")

    requirements: list[str] = Field(..., description="The requirements extracted from the client request.")


class ProjectState(ProjectStateInit):
    client_request: str = Field(..., description="The client request that initiated the project.")
    goal: str = Field(..., description="The goal of the project.")

    requirements: list[str] = Field(..., description="The requirements extracted from the client request.")

    current_sprint: Sprint | None = Field(None, description="The current sprint of the project.")
    sprint_history: list[SprintResult] = Field([], description="The results of sprints that have been completed.")
