from abc import ABC, abstractmethod


class Tool(ABC):
    @abstractmethod
    def call(self, *args, **kwargs): ...
