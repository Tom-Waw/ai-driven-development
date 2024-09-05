from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_dir: Path
    template_dir: Path

    openai_api_key: str
    openai_model_name: str = "gpt-4o-mini"


settings = Settings()
