from abc import ABC, abstractmethod
from tools.tools import partial_register_tool
from typing import List

from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent

from lpu.standard import base_config, is_termination_message


class Team(ABC):
    def __init__(self, *args, **kwargs):
        self.user_proxy = UserProxyAgent(
            name="User_Proxy",
            human_input_mode="NEVER",
            is_termination_msg=is_termination_message,
            code_execution_config=False,
        )

        self.register_skill = partial_register_tool(self.user_proxy)
        self.agents = self.init_agents(*args, **kwargs)

        self.recipient = self.init_recipient()

    @abstractmethod
    def init_agents(self, *args, **kwargs) -> List[ConversableAgent]: ...

    def init_recipient(self) -> ConversableAgent | GroupChatManager:
        groupchat = GroupChat(
            agents=[self.user_proxy, *self.agents],
            messages=[],
            max_round=50,
        )
        return GroupChatManager(
            groupchat,
            llm_config=base_config,
            is_termination_msg=is_termination_message,
            code_execution_config=False,
        )
