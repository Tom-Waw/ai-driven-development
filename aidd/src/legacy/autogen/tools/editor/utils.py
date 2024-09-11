from functools import wraps
from pathlib import Path

from ram import editor
from settings import settings


class AccessDeniedError(Exception):
    pass


def validate_path(path: str | None = None):
    if path is None:
        path = "."

    if Path(path).is_absolute():
        raise AccessDeniedError(f"Access denied: Absolute path {path} is not allowed.")

    full_path = (settings.project_dir / path).resolve()
    if not full_path.is_relative_to(settings.project_dir):
        raise AccessDeniedError(f"Access denied: Attempted access outside of project directory at path: {path}")

    return full_path


def valid_path(func):
    """Decorator to validate the path."""

    @wraps(func)
    def wrapper(*args, path: str | None = "", **kwargs):
        # Join path overlapping with the project directory
        subpath = Path(path or "")
        full_path = editor.workspace / subpath

        if not full_path.is_relative_to(settings.project_dir):
            raise ValueError(f"Access denied: Attempted access outside of working directory at path: {path}")

        if full_path.is_symlink():
            raise ValueError(f"Security alert: Path is a symbolic link at path: {path}")

        return func(full_path, *args, **kwargs)

    wrapper.__annotations__["path"] = str | None
    return wrapper
