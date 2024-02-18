from pathlib import Path


class Settings:
    WORK_DIR = Path.cwd() / "session"
    CODE_DIR = WORK_DIR / "code"
    TEST_DIR = WORK_DIR / "tests"
    REQUIREMENTS_FILE = WORK_DIR / "requirements.txt"
