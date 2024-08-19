from lpu.llm.abc import LLM, LLMModel
from openai import OpenAI


class ChatGPTModel(LLMModel):
    GTP4_MINI = "gpt-4o-mini"


class ChatGPT(LLM):
    client = OpenAI()

    def __init__(self, model: ChatGPTModel) -> None:
        self.model = model

    def query(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1080,
            temperature=0,
        )

        response = response.choices[0].message
        if response.content is None:
            raise ValueError(f"Unexpected response: {response}")

        return response.content
