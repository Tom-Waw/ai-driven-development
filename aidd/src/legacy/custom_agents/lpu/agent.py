import openai
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel
from tools.abc import Tool

from . import logger


class Agent:
    def __init__(
        self,
        name: str = "Assistant",
        model: str = "gpt-4o-mini",
        system_message: str | None = None,
        max_messages: int = 15,
        tools: list[type[Tool]] = [],
    ) -> None:
        self.name = name
        logger.debug(f"Initializing {self.name}")

        self.model = model
        self.client = openai.OpenAI()
        self.system_message = system_message
        self.max_messages = max_messages

        ### Tools ###
        self.tool_schema = [tool.openai_schema() for tool in tools]
        self.tools = {schema["function"]["name"]: tool for tool, schema in zip(tools, self.tool_schema)}

        ### Messages ###
        self.messages: list[ChatCompletionMessageParam] = []
        self.init_messages()

    def init_messages(self, messages: list[ChatCompletionMessageParam] = []) -> None:
        self.messages.clear()
        if self.system_message:
            self.messages.append(
                ChatCompletionSystemMessageParam(
                    role="system",
                    content=self.system_message,
                )
            )

        self.messages.extend(messages)

    def reset(self) -> None:
        self.init_messages()

    def prompt(
        self,
        prompt: str | None,
        use_tools: bool = True,
        response_format: BaseModel | None = None,
    ) -> ChatCompletionMessage:
        if prompt:
            logger.debug(f"{self.name} prompted with:\n{prompt}")
            self.messages.append(
                ChatCompletionUserMessageParam(
                    role="user",
                    content=prompt,
                )
            )

        # Generate response
        optional_args = {}
        if use_tools and self.tool_schema:
            optional_args["tools"] = self.tool_schema
        if response_format:
            optional_args["response_format"] = response_format

        response = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=0,
            messages=self.messages,
            **optional_args,
        )
        message = response.choices[0].message

        # ! Bug fix: OpenAI API returns empty list, which is not valid JSON
        if not message.tool_calls:
            message.tool_calls = None

        logger.debug(f"{self.name} responded:\n{message.model_dump_json(indent=2)}")

        # Append response to memory
        self.messages.append(ChatCompletionAssistantMessageParam(**message.model_dump()))

        # Call tools
        tool_calls = message.tool_calls or []
        for tc in tool_calls:
            logger.debug(f"Tool {tc.function.name} calling with arguments:\n{tc.function.arguments}")

            tool: Tool = tc.function.parsed_arguments
            assert isinstance(tool, Tool)

            try:
                result = tool.call()
            except Exception as e:
                result = str(e)

            logger.debug(f"Tool {tc.function.name} responded:\n{result}")
            self.messages.append(
                ChatCompletionToolMessageParam(
                    role="tool",
                    content=result,
                    tool_call_id=tc.id,
                )
            )

        if len(self.messages) > self.max_messages:
            keep = self.messages[-self.max_messages :]
            # ? Remove tools from the beginning of the list as they need to be called in the chat
            while True:
                if keep[0].get("role") != "tool":
                    break
                keep.pop(0)

            self.init_messages(keep)

        return message
