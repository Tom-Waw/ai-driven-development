from functools import wraps
from pathlib import Path

from ram.ticket_system import Ticket
from settings import settings

### EDITOR ###


def get_full_overlapping_path(path: str) -> Path:
    """Get the full path overlapping with the project directory."""
    subpath = Path(path)
    if settings.project_dir in subpath.parents:
        return subpath
    return settings.project_dir / subpath


def validate_path(path: str | None = None) -> Path:
    """Validate the path."""
    if not path:
        return settings.project_dir

    full_path = get_full_overlapping_path(path)

    if not full_path.is_relative_to(settings.project_dir):
        raise ValueError(f"Access denied: Attempted access outside of working directory at path: {path}")

    if full_path.is_symlink():
        raise ValueError(f"Security alert: Path is a symbolic link at path: {path}")

    return full_path


def valid_path(func):
    """Decorator to validate the path."""

    @wraps(func)
    def wrapper(*args, path: str | None = "", **kwargs):
        full_path = get_full_overlapping_path(path)
        return func(full_path, *args, **kwargs)

    wrapper.__annotations__["path"] = str | None
    return wrapper


### SCRUM ###


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
