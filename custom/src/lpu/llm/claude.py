import anthropic
import anthropic.types
from lpu.llm.abc import LLM, LLMModel


class ClaudeModel(LLMModel):
    SONNET = "claude-3-5-sonnet-20240620"


class Claude(LLM):
    client = anthropic.Anthropic()

    def __init__(self, model: ClaudeModel) -> None:
        self.model = model

    def query(self, messages: list) -> str:
        message = self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=1080,
            temperature=0,
        )

        content = message.content[0]
        if content.type != "text":
            raise ValueError(f"Unexpected content type: {content}")

        return content.text
