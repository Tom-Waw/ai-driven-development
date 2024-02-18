from abc import ABC
from typing import List

from autogen import ConversableAgent, UserProxyAgent

USER_PROXY_PROMPT = "A human admin. Discuss the plan. Plan execution needs to be approved by this admin."


class Team(ABC):
    @classmethod
    def build_agents(cls, *args, **kwargs) -> List[ConversableAgent]:
        return [
            UserProxyAgent(
                name="Admin",
                system_message=USER_PROXY_PROMPT,
                code_execution_config=False,
                human_input_mode="NEVER",
            )
        ]
