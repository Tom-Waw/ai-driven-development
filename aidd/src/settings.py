from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_dir: Path
    project_skeleton_dir: Path


settings = Settings()
