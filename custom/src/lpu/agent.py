from typing import Sequence

from lpu.formatting.abc import PromptFormatter
from lpu.formatting.history_formatter import HistoryFormatter
from lpu.formatting.template_formatter import TemplateFormatter
from lpu.llm.abc import LLM
from lpu.llm.chatgpt import ChatGPT, ChatGPTModel
from lpu.parsing.abc import ResponseParser, Trigger
from lpu.parsing.coding_parser import CodingParser
from lpu.parsing.json_parser import JSONResponseParser

from . import logger

DEFAULT_LLM = ChatGPT(model=ChatGPTModel.GTP4_MINI)
DEFAULT_PROMPT_FORMATTERS = [TemplateFormatter(), HistoryFormatter()]
DEFAULT_RESPONSE_PARSERS = [JSONResponseParser(), CodingParser()]


class Agent:
    def __init__(
        self,
        name: str,
        llm: LLM = DEFAULT_LLM,
        system_message: str | None = None,
        prompt_formatters: Sequence[PromptFormatter] = DEFAULT_PROMPT_FORMATTERS,
        response_parsers: Sequence[ResponseParser] = DEFAULT_RESPONSE_PARSERS,
    ) -> None:
        self.name = name
        self._llm = llm
        self._system_message = system_message
        self._prompt_formatters = prompt_formatters
        self._response_parsers = response_parsers

    def prompt(self, prompt: str, context: dict | None = None) -> dict:
        context = context or {}
        prompt = self._format_prompt(prompt, context)
        logger.debug(f"{self.name} prompted:\n{prompt}")

        # TODO: Add system prompt, decribing tools and capabilities
        messages = self.construct_llm_messages(prompt)
        logger.debug(f"{self.name} sent messages:\n{messages}")
        response = self._llm.query(messages)
        logger.debug(f"{self.name} responded:\n{response}")

        self._parse_response(response, context)
        logger.debug(f"{self.name} updated context:\n{context}")

        # TODO: Trigger functions from context

        return {
            "prompt": prompt,
            "response": response,
            "context": context,
        }

    def construct_llm_messages(self, prompt: str) -> list:
        messages = []

        if self._system_message:
            messages.append(
                {
                    "role": "system",
                    "content": self._system_message,
                }
            )

        messages += [
            {
                "role": "system",
                "content": parser.description,
            }
            for parser in self._response_parsers
        ]

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return messages

    def _format_prompt(self, prompt: str, context: dict) -> str:
        for formatter in self._prompt_formatters:
            prompt = formatter.format(prompt, context)

        return prompt

    def _parse_response(self, response: str, context: dict) -> None:
        for parser in self._response_parsers:
            parser.parse(response, context)

    def _take_action(self, context: dict) -> None:
        triggers: list[Trigger] = []
        for parser in self._response_parsers:
            triggers += context[parser.response_field][-1]

        triggers = list(filter(lambda t: isinstance(t, Trigger), triggers))
        triggers = sorted(triggers, key=lambda t: t.pos)

        for trigger in triggers:
            # trigger.action(context)
            pass

    # def prompt_chain(self, prompts: Sequence[str], context: dict | None = None) -> str:
    #     context = context or {}
    #     if not prompts:
    #         raise ValueError("At least one prompt is required")

    #     output = []
    #     for prompt in prompts:
    #         context["output"] = output  # Update context with previous output
    #         response = self.prompt(prompt, context)
    #         # TODO: Add response from function calls to output
    #         output.append(response)

    #     return output[-1]
