from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class IDGen:
    id_gen: int = 0

    def next_id(self) -> int:
        self.id_gen += 1
        return self.id_gen


class TicketStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    REVIEW = "review"
    DONE = "done"


class Ticket(BaseModel):
    id: int = Field(default_factory=IDGen().next_id, init=False)
    title: str
    description: str
    condition: str  # for accespability
    status: TicketStatus = Field(default=TicketStatus.BACKLOG, init=False)

    def __format__(self, __format_spec: str) -> str:
        match __format_spec:
            case "details":
                return "\n".join(
                    (
                        f"{self}",
                        "Description:",
                        self.description,
                        "Condition:",
                        self.condition,
                    )
                )
            case _:
                return f"{self.id} | {self.title} (Status: {self.status})"


class TicketSystem(BaseModel):
    tickets: List[Ticket] = Field(default_factory=list)

    @property
    def backlog(self) -> List[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.BACKLOG]

    @property
    def sprint(self) -> List[Ticket]:
        sprint = [ticket for ticket in self.tickets if ticket.status not in [TicketStatus.BACKLOG, TicketStatus.DONE]]
        return sorted(sprint, key=lambda ticket: ticket.status)

    @property
    def done(self) -> List[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.DONE]

    def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        return next((ticket for ticket in self.tickets if ticket.id == ticket_id), None)
