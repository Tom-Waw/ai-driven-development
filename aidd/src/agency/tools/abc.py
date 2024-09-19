from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic import BaseModel


class CustomTool(BaseModel, ABC):
    name: str
    description: str

    @property
    @abstractmethod
    def run(self) -> Callable: ...
