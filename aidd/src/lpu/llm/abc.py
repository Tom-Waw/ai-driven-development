from abc import ABC, abstractmethod
from enum import Enum


class LLMModel(str, Enum): ...


class LLM(ABC):
    @property
    @abstractmethod
    def query(self): ...
