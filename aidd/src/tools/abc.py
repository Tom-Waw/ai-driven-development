from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class Tool(BaseModel, ABC):

    @classmethod
    def openai_schema(cls) -> dict[str, Any]:
        """Return the OpenAI schema for the tool."""
        schema = cls.model_json_schema()

        return {
            "type": "function",
            "function": {
                "name": schema.pop("title"),
                "description": schema.pop("description"),
                "parameters": schema,
            },
        }

    @abstractmethod
    def call(self) -> str: ...


