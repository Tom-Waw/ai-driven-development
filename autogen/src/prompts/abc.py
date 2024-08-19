from abc import ABC
from typing import ClassVar

from pydantic import BaseModel


class Template(ABC):
    template: ClassVar[str]

    @classmethod
    def render(cls, **kwargs) -> str:
        """Render the template with the given kwargs and send the message to the recipient."""
        prompt = cls.template
        for key, value in kwargs.items():
            replacement: str
            if isinstance(value, BaseModel):
                replacement = value.model_dump_json(indent=4)
            else:
                replacement = str(value)

            prompt = prompt.replace("{{" + key + "}}", replacement)

        return prompt
