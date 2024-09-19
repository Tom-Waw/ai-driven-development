from enum import Enum

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    TODO = "todo"
    DONE = "done"
    FAILED = "failed"


class Ticket(BaseModel):
    title: str = Field(..., description="A short title for the ticket.")
    description: str = Field(..., description="A detailed description of what needs to be done.")
    expectation: str = Field(..., description="The expected outcome of the ticket.")
    acceptance_criteria: str = Field(
        ..., description="The criteria that need to be met for the ticket to be considered done."
    )
    status: TicketStatus = TicketStatus.TODO


class Sprint(BaseModel):
    goal: str = Field(..., description="The goal of the sprint.")
    tickets: list[Ticket] = Field(default_factory=list, description="The tickets in the sprint.")

    @property
    def open_tickets(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.TODO]

    @property
    def completed_tickets(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.status == TicketStatus.DONE]

    def get_ticket_by_id(self, ticket_id: int) -> Ticket | None:
        return next((ticket for ticket in self.tickets if ticket.id == ticket_id), None)
