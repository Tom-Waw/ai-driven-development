import os


class Settings:
    WORK_DIR = os.getcwd()
    CODE_DIR = os.path.join(WORK_DIR, "output")
    TEST_DIR = os.path.join(WORK_DIR, "tests")
    REQUIREMENTS_FILE = os.path.join(WORK_DIR, "requirements.txt")
