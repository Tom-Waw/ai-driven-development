from typing import Annotated

from ram import ticket_system
from ram.ticket_system import Ticket, TicketStatus

### CREATE ###


def create_ticket(ticket: Annotated[Ticket, "The ticket to add to the backlog."]) -> str:
    """Adds a ticket to the backlog."""
    ticket_system.tickets.append(ticket)
    return f"Ticket {ticket.id} added to the backlog."


### READ ###


def show_backlog() -> str:
    """Lists all the tickets in the backlog with their ids."""
    return "\n".join([f"{ticket}" for ticket in ticket_system.backlog])


def show_sprint() -> str:
    """Lists all the tickets in the sprint with their ids."""
    return "\n".join([f"{ticket}" for ticket in ticket_system.sprint])


def read_ticket_details(ticket_id: Annotated[int, "The unique id of the ticket."]) -> str:
    """Reads the details of a ticket."""
    ticket = ticket_system.get_ticket_by_id(ticket_id)
    if ticket is None:
        return "Ticket not found."

    return f"{ticket:details}"


### UPDATE ###


def ticket_to_sprint(ticket_id: Annotated[int, "The unique id of the ticket in the backlog."]) -> str:
    """Moves a ticket from the backlog to the sprint."""
    ticket = ticket_system.get_ticket_by_id(ticket_id)
    if ticket is None:
        return "Ticket not found."

    ticket.status = TicketStatus.TODO
    return f"Ticket {ticket.id} moved to the sprint."


### DELETE ###


def delete_ticket(ticket_id: Annotated[int, "The unique id of the ticket."]) -> str:
    """Deletes a ticket. Only do this if you're sure!"""
    ticket = ticket_system.get_ticket_by_id(ticket_id)
    if ticket is None:
        return "Ticket not found."

    ticket_system.tickets.remove(ticket)
    return f"Ticket {ticket.id} deleted."
