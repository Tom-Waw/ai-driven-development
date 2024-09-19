from typing import Callable

from agency.tools.abc import CustomTool
from state.project_state import ProjectState
from state.sprint import Sprint, Ticket, TicketCreate, TicketStatus

### CREATE ###


class SetSprintGoal(CustomTool):
    name: str = "set_sprint_goal"
    description: str = "Initiate a new sprint with a goal."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run(goal: str) -> str:
            self.state.current_sprint = Sprint(goal=goal)
            return f"New sprint initiated. You can now add tickets to the sprint."

        return _run


class AddTicket(CustomTool):
    name: str = "add_ticket"
    description: str = "Add a ticket to the next sprint."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run(new_ticket: TicketCreate) -> str:
            ticket = Ticket.model_validate(new_ticket, from_attributes=True)
            self.state.current_sprint.tickets.append(ticket)

            return f"Ticket {ticket.id} added to the sprint."

        return _run


### READ ###


def format_ticket(ticket: Ticket, detailed: bool = False) -> str:
    """Format a ticket."""
    output = f"{ticket.id} | {ticket.title} (Status: {ticket.status})"
    if not detailed:
        return output

    return "\n".join(
        (
            output,
            "Description:",
            ticket.description,
            "Condition:",
            ticket.acceptance_criteria,
        )
    )


class ShowTickets(CustomTool):
    name: str = "show_tickets"
    description: str = "Show the open tickets in the sprint."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run() -> str:
            return "\n".join([format_ticket(ticket) for ticket in self.state.current_sprint.open_tickets])

        return _run


class ReadTicketDetails(CustomTool):
    name: str = "read_ticket_details"
    description: str = "Read the details of a ticket."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run(ticket_id: int) -> str:
            ticket = self.state.current_sprint.get_ticket_by_id(ticket_id)
            if ticket is None:
                return "Ticket not found."

            return format_ticket(ticket, detailed=True)

        return _run


### UPDATE ###


class UpdateTicketStatus(CustomTool):
    name: str = "update_ticket_status"
    description: str = "Update the status of a ticket."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run(ticket_id: int, status: TicketStatus) -> str:
            ticket = self.state.current_sprint.get_ticket_by_id(ticket_id)
            if ticket is None:
                return "Ticket not found."

            ticket.status = status
            return f"Ticket {ticket.id} moved to {status}."

        return _run


### DELETE ###


class DeleteTicket(CustomTool):
    name: str = "delete_ticket"
    description: str = "Delete a ticket from the sprint."
    state: ProjectState

    @property
    def run(self) -> Callable:
        def _run(ticket_id: int) -> str:
            ticket = self.state.current_sprint.get_ticket_by_id(ticket_id)
            if ticket is None:
                return "Ticket not found."

            self.state.current_sprint.tickets.remove(ticket)
            return f"Ticket {ticket.id} deleted from the sprint."

        return _run
