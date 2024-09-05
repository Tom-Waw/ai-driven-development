from abc import ABC, abstractmethod
from typing import Any

from openai import pydantic_function_tool
from pydantic import BaseModel


class Tool(BaseModel, ABC):

    @classmethod
    def openai_schema(cls) -> dict[str, Any]:
        """Return the OpenAI schema for the tool."""
        schema = pydantic_function_tool(cls)

        # ! FIX: double assignment of title and description
        schema["function"]["parameters"].pop("title", None)
        descritpion = schema["function"]["parameters"].pop("description", None)
        if descritpion:
            schema["function"]["description"] = descritpion

        return schema

    @abstractmethod
    def call(self) -> str: ...
