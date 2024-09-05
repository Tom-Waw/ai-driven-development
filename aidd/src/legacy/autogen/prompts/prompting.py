from prompts.abc import Template
from pydantic import BaseModel

from autogen import Agent, ConversableAgent


class HistoryEntry(BaseModel):
    prompt: str
    result: BaseModel | None = None


class PromptingEngine:
    def __init__(self):
        self.history: dict[str, HistoryEntry] = {}

    def call_template(self, id: str, template: type[Template], source: str | None = None, **kwargs):
        def func(sender: str, recipient: str, config: dict) -> str:
            if source is not None:
                if source not in self.history:
                    raise ValueError(f"Source '{source}' not found in the history.")

                prev_result = self.history[source].result
                if prev_result is None:
                    raise ValueError(f"Source '{source}' has no result to use in the template.")

                kwargs.update(prev_result.model_dump())

            prompt = template.render(**kwargs)
            self.history[id] = HistoryEntry(prompt=prompt)
            return prompt

        return func

    def get_result(self, id: str, template: type[Template]):
        def func(sender: Agent, recipient: ConversableAgent, summary_args: dict) -> str:
            last_message = ConversableAgent._last_msg_as_summary(sender, recipient, summary_args)
            if template.result_model is None:
                raise ValueError("Template has no result model to validate the last message.")

            result = template.result_model.model_validate_json(last_message)
            self.history[id].result = result

            return ""

        return func
