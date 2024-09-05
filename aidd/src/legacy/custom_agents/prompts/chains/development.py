from lpu.agent import Agent
from ram.ticket_system import Ticket


def run_development_chain(ticket: Ticket) -> None:
    agent = Agent(
        "Developer",
        system_message="You are a software developer working on a new feature. "
        + "You are especially profounded in python.",
    )

    
