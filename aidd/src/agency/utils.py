from pathlib import Path

from settings import settings


class AccessDeniedError(Exception):
    pass


def validate_path(path: str | None = None) -> Path:
    if path is None:
        path = "."

    if Path(path).is_absolute():
        raise AccessDeniedError(f"Access denied: Absolute path {path} is not allowed.")

    full_path = (settings.project_dir / path).resolve()
    if not full_path.is_relative_to(settings.project_dir):
        raise AccessDeniedError(f"Access denied: Attempted access outside of project directory at path: {path}")

    return full_path
