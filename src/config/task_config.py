from config import load_config
from errors.config_errors import ConfigError

TASK_CONFIG_FILE = "tasks.yml"


def load_task(name: str) -> str:
    task_config = load_config(TASK_CONFIG_FILE)

    if task_config is None:
        raise ConfigError("Empty task config.", "task")

    if name not in task_config:
        raise ConfigError("Task not found.", "task")

    return task_config[name]
