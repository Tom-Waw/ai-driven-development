from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_dir: Path
    template_dir: Path
    ignore_dirs: list[str] = [".git", "venv", "__pycache__"]

    openai_api_key: str
    openai_model_name: str = "gpt-4o-mini"

    main_branch: str = "main"
    ticket_prefix: str = "ticket-"


settings = Settings()
