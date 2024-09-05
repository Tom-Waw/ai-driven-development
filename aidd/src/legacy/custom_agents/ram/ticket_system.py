from enum import Enum

from pydantic import BaseModel, Field


class IDGen:
    id_gen: int = 0

    def next_id(self) -> int:
        self.id_gen += 1
        return self.id_gen


class TicketStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    DONE = "done"


class Ticket(BaseModel):
    id: int = Field(default_factory=IDGen().next_id, init=False)
    title: str
    description: str
    expectation: str
    acceptance_criteria: str
    status: TicketStatus = TicketStatus.TODO


class Sprint(BaseModel):
    goal: str
    tickets: list[Ticket] = Field(default_factory=list)

    @property
    def open_tickets(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.TODO]

    @property
    def completed_tickets(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.DONE]

    def get_ticket_by_id(self, ticket_id: int) -> Ticket | None:
        return next((ticket for ticket in self.tickets if ticket.id == ticket_id), None)


# class TicketSystem(BaseModel):
#     tickets: list[Ticket] = Field(default_factory=list)

#     @property
#     def backlog(self) -> list[Ticket]:
#         return [ticket for ticket in self.tickets if ticket.status == TicketStatus.BACKLOG]

#     @property
#     def sprint(self) -> list[Ticket]:
#         sprint = [ticket for ticket in self.tickets if ticket.status not in [TicketStatus.BACKLOG, TicketStatus.DONE]]
#         return sorted(sprint, key=lambda ticket: ticket.status)

#     @property
#     def done(self) -> list[Ticket]:
#         return [ticket for ticket in self.tickets if ticket.status == TicketStatus.DONE]

#     def get_ticket_by_id(self, ticket_id: int) -> Ticket | None:
#         return next((ticket for ticket in self.tickets if ticket.id == ticket_id), None)
