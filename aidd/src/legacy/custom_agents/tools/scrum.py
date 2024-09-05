from typing import Literal

from pydantic import Field
from ram import ticket_system
from ram.ticket_system import Ticket, TicketStatus
from tools.abc import Tool
from tools.utils import format_ticket

tools: list[Tool] = []


def register_tool(tool: type[Tool]) -> type[Tool]:
    tools.append(tool)
    return tool


### CREATE ###


@register_tool
class CreateTicket(Tool, Ticket):
    """Create a ticket and add it to the backlog."""

    def call(self) -> str:
        ticket = Ticket.model_validate(self, from_attributes=True)
        ticket_system.tickets.append(ticket)
        return f"Ticket {self.id} added to the backlog."


### READ ###


@register_tool
class ShowTickets(Tool):
    """Show the tickets in a specific log."""

    log: Literal["backlog", "sprint", "done"] = Field("backlog", description="The log to show.")

    def call(self) -> str:
        tickets = {
            "backlog": ticket_system.backlog,
            "sprint": ticket_system.sprint,
            "done": ticket_system.done,
        }[self.log]
        return "\n".join([format_ticket(ticket) for ticket in tickets])


@register_tool
class ReadTicketDetails(Tool):
    """Read the details of a ticket."""

    ticket_id: int = Field(..., description="The unique id of the ticket.")

    def call(self) -> str:
        ticket = ticket_system.get_ticket_by_id(self.ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found.")

        return format_ticket(ticket, detailed=True)


### UPDATE ###


@register_tool
class MoveTicket(Tool):
    """Change the status of a ticket."""

    ticket_id: int = Field(..., description="The unique id of the ticket in the backlog.")
    status: TicketStatus = Field(TicketStatus.TODO, description="The new status of the ticket.")

    def call(self) -> str:
        ticket = ticket_system.get_ticket_by_id(self.ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found.")

        ticket.status = self.status
        return "Status updated."


### DELETE ###


@register_tool
class DeleteTicket(Tool):
    """Delete a ticket from the project. Use with caution!"""

    ticket_id: int = Field(..., description="The unique id of the ticket.")

    def call(self) -> str:
        ticket = ticket_system.get_ticket_by_id(self.ticket_id)
        if ticket is None:
            raise ValueError("Ticket not found.")

        ticket_system.tickets.remove(ticket)
        return "Ticket deleted permanently."
