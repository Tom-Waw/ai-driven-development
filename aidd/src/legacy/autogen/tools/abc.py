from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel


class Tool(BaseModel, ABC):
    description: ClassVar[str]
    arguments: ClassVar[BaseModel]

    @abstractmethod
    def execute(self, *args, **kwargs): ...
