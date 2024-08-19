from abc import ABC, abstractmethod
from enum import Enum


class LLMModel(str, Enum): ...


class LLM(ABC):
    @abstractmethod
    def query(self, messages: list) -> str: ...
