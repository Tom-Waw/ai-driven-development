from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class IDGenerator:
    id_gen: int = 0

    @classmethod
    def next_id(cls) -> int:
        cls.id_gen += 1
        return cls.id_gen


class TicketStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    TEST_PHASE = "test_phase"
    IMPLEMENTATION_PHASE = "implementation_phase"
    REVIEW_PHASE = "review_phase"
    DONE = "done"


class Ticket(BaseModel):
    id: int = Field(default_factory=IDGenerator.next_id)
    title: str
    description: str
    status: TicketStatus = TicketStatus.BACKLOG

    def __format__(self, __format_spec: str) -> str:
        match __format_spec:
            case "details":
                return f"{self}\nDescription:\n{self.description}"
            case _:
                return f"{self.id} | {self.title} (Status: {self.status})"


class Project(BaseModel):
    name: str
    goal: str
    tickets: list[Ticket] = []

    @property
    def backlog(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.BACKLOG]

    @property
    def sprint(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status not in [TicketStatus.BACKLOG, TicketStatus.DONE]]

    @property
    def done(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.DONE]


project: Project


def create_project(
    name: Annotated[str, "The name of the project"], goal: Annotated[str, "The goal of the project"]
) -> str:
    """Create a new project."""
    global project

    project = Project(name=name, goal=goal)
    return f"Project {name} created successfully."


def create_ticket(
    title: Annotated[str, "The title of the ticket"], description: Annotated[str, "The description of the ticket"]
) -> str:
    """Create a new task and add it to the project backlog."""
    global project
    if project is None:
        return "No project created yet."

    ticket = Ticket(title=title, description=description)
    project.tickets.append(ticket)

    return f"Ticket {ticket.id} added to the backlog."


def show_backlog() -> str:
    """List all the tickets in the backlog with their ids."""
    global project
    if project is None:
        return "No project created yet."

    return "\n".join([f"{ticket}" for ticket in project.backlog])


def read_ticket_details(ticket_id: Annotated[int, "The unique id of the ticket"]) -> str:
    """Read the details of a ticket."""
    global project
    if project is None:
        return "No project created yet."

    ticket = next((ticket for ticket in project.tickets if ticket.id == ticket_id), None)
    if ticket is None:
        return "Ticket not found."

    return f"{ticket:details}"


def delete_ticket(ticket_id: Annotated[int, "The unique id of the ticket"]) -> str:
    """Delete a ticket."""
    global project
    if project is None:
        return "No project created yet."

    ticket = next((ticket for ticket in project.tickets if ticket.id == ticket_id), None)
    if ticket is None:
        return "Ticket not found."

    return f"Ticket {ticket.id} deleted."


def ticket_to_sprint(ticket_id: Annotated[int, "The unique id of the ticket in the backlog"]) -> str:
    """Move a ticket from the backlog to the sprint."""
    global project
    if project is None:
        return "No project created yet."

    ticket = next((ticket for ticket in project.backlog if ticket.id == ticket_id), None)
    if ticket is None:
        return "Ticket not found."

    ticket.status = TicketStatus.TODO

    return f"Ticket {ticket.id} moved to the sprint."


def show_sprint() -> str:
    """List all the tickets in the current sprint with their id and status."""
    global project
    if project is None:
        return "No project created yet."

    tickets_by_status = sorted(project.sprint, key=lambda ticket: ticket.status)
    return "\n".join([f"{ticket}" for ticket in tickets_by_status])
