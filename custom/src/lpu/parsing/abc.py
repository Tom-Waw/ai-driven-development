from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ResponseParser(ABC):
    """Abstract base class for response parsers."""

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def response_field(self) -> str: ...

    @abstractmethod
    def parse(self, response: str, context: dict) -> None: ...


class Trigger(BaseModel):
    pos: int
