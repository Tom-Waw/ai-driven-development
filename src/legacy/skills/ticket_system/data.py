from enum import Enum

from pydantic import BaseModel


class TicketStatus(str, Enum):
    TODO = "todo"
    TEST_PHASE = "test_phase"
    IMPLEMENTATION_PHASE = "implementation_phase"
    REVIEW_PHASE = "review_phase"
    DONE = "done"


class Ticket(BaseModel):
    title: str
    description: str
    priority: int = 0
    status: TicketStatus = TicketStatus.TODO
    assignee: str | None = None


class Project(BaseModel):
    name: str
    goal: str
    backlog: list[Ticket] = []
    sprint: list[Ticket] = []
    done: list[Ticket] = []


ProjectState: Project | None = None

