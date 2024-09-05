from typing import Any

from pydantic import BaseModel


class Template:
    def __init__(self, template: str):
        self.template = template

    def render(self, input: BaseModel | None = None, **kwargs) -> str:
        """Render the template with the given kwargs and send the message to the recipient."""
        prompt = self.template
        if input:
            flat = self.flatten_input(input.model_dump())
            kwargs.update(flat)

        for key, value in kwargs.items():
            prompt = prompt.replace("{{" + key + "}}", str(value))

        return prompt

    def flatten_input(self, input: dict[str, Any], prefix: str = "") -> dict:
        """Flattens a dictionary to a list of tuples (key.key.key, value)."""
        flat = {}
        for key, value in input.items():
            flat[prefix + key] = value

            if isinstance(value, dict):
                nested = self.flatten_input(value, prefix + key + ".")
                flat.update(nested)

        return flat
