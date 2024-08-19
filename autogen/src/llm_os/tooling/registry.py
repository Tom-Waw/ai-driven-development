from collections.abc import Callable

from autogen import ConversableAgent, agentchat


class ToolRegistry:
    def __init__(self, name: str):
        self.name = name
        self._tools = []

    @property
    def tools(self):
        return self._tools

    def register(self, func):
        self._tools.append(func)
        return func

    def assign(self, proxy: ConversableAgent, *agents: ConversableAgent) -> None:
        for tool in self._tools:
            self._single_assign(tool, proxy, *agents)

    def _single_assign(self, tool: Callable, proxy: ConversableAgent, *agents: ConversableAgent) -> None:
        if tool.__doc__ is None:
            raise ValueError(f"The skill {tool.__name__} has no docstring.")

        for agent in agents:
            agentchat.register_function(
                tool,
                caller=agent,
                executor=proxy,
                description=tool.__doc__,
            )
