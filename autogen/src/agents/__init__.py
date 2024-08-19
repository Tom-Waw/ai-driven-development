from llm_os.lpu.standard import (
    PROMPT_APPRECIATION_CONSTRAINT,
    PROMPT_END_CONVERSATION,
    base_config,
    is_termination_message,
)

from autogen import ConversableAgent


def create_assistant(name: str = "Assistant", system_message: str = "") -> ConversableAgent:
    return ConversableAgent(
        name=name,
        system_message=system_message + PROMPT_END_CONVERSATION + PROMPT_APPRECIATION_CONSTRAINT,
        llm_config=base_config,
        is_termination_msg=is_termination_message,
    )
