import shutil
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_dir: Path = Path("/home/app/code")
    template_dir: Path = Path("/home/app/template")
    ignore_dirs: list[str] = [".git", "venv", "__pycache__", ".pytest_cache"]

    openai_api_key: str
    openai_model_name: str = "gpt-4o-mini"

    logfile: str = "logs"


settings = Settings()


def reset() -> None:
    # Reset the project directory
    for item in settings.project_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    shutil.copytree(settings.template_dir, settings.project_dir, dirs_exist_ok=True)

    print("Project reset.")
