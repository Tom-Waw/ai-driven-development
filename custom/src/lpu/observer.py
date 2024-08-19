import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Role(str, Enum):
    USER = "USER"
    AGENT = "AGENT"


@dataclass
class ObserverMessage:
    role: Role
    agent: str
    message: Any


class PromptObserver:
    """Class to observe the prompting steps and results of the Agents."""

    ROOT_DIR = "/logs"

    def __init__(self):
        self.messages = []

    def reset(self):
        self.messages = []

    def update(self, agent: str, role: Role, message: Any):
        message = ObserverMessage(role, agent, str(message))
        logging.info(f"{message.role} -> {message.agent}:\n{message.message}")
        self.messages.append(message)

    def to_file(self, filename: str):
        content = ""
        for message in self.messages:
            # Role talking with agent
            content += f"{message.role} -> {message.agent}:\n"
            content += message.message
            content += "\n\n"

        with open(f"{self.ROOT_DIR}/{filename}", "w") as f:
            f.write(content)
