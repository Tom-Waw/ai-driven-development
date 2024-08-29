import openai
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam
from pydantic import BaseModel
from tools.abc import Tool

from . import logger


class Agent:
    def __init__(
        self,
        name: str = "Assistant",
        model: str = "gpt-4o-mini",
        system_message: str | None = None,
        tools: list[type[Tool]] = [],
    ) -> None:
        self.name = name
        logger.debug(f"Initializing {self.name}")

        self.model = model
        self.client = openai.OpenAI()
        self.system_message = system_message

        ### Tools ###
        self.tool_schema = [tool.openai_schema() for tool in tools]
        self.tools = {schema["function"]["name"]: tool for tool, schema in zip(tools, self.tool_schema)}

        ### Messages ###
        self.messages: list[ChatCompletionMessageParam] = []
        self.init_messages()

    def init_messages(self) -> None:
        self.messages.clear()
        if self.system_message:
            self.messages.append(
                {
                    "role": "system",
                    "content": self.system_message,
                }
            )

    def prompt(
        self,
        prompt: str,
        use_tools: bool = True,
        response_format: BaseModel | None = None,
    ) -> ChatCompletionMessage:
        logger.debug(f"{self.name} prompted with:\n{prompt}")
        self.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
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
            max_tokens=1080,
            messages=self.messages,
            **optional_args,
        )
        message = response.choices[0].message

        # ! Bug fix: OpenAI API returns empty list, which is not valid JSON
        if not message.tool_calls:
            message.tool_calls = None

        logger.debug(f"{self.name} responded:\n{message.model_dump_json(indent=2)}")

        # Append response to memory
        self.messages.append(message)

        # Call tools
        tool_calls = message.tool_calls or []
        for tc in tool_calls:
            tool = self.tools[tc.function.name].model_validate_json(tc.function.arguments)
            logger.debug(f"Tool {tc.function.name} calling with arguments:\n{tc.function.arguments}")
            try:
                result = tool.call()
            except Exception as e:
                result = str(e)

            logger.debug(f"Tool {tc.function.name} responded:\n{result}")

            tool_response = {"role": "tool", "content": result, "tool_call_id": tc.id}
            self.messages.append(tool_response)

        return message
