from typing import Callable

from autogen import ConversableAgent, agentchat


def register_tool(proxy: ConversableAgent, tool: Callable, *agents: ConversableAgent) -> None:
    if tool.__doc__ is None:
        raise ValueError(f"The skill {tool.__name__} has no docstring.")

    for agent in agents:
        agentchat.register_function(
            tool,
            caller=agent,
            executor=proxy,
            description=tool.__doc__,
        )
