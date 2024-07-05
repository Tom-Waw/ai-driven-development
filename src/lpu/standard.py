from autogen import config_list_from_json

config_list = config_list_from_json(env_or_file="../OAI_CONFIG_LIST.json")

base_config = {
    "config_list": config_list,
    "cache_seed": None,
    "temperature": 0,
}


TERMINATION_SYMBOL = "TERMINATE"

PROMPT_APPRECIATION_CONSTRAINT = "\nDo not show any appreciation in your responses."
PROMPT_END_CONVERSATION = f"\nReply '{TERMINATION_SYMBOL}' if the task has been solved at full satisfaction."


def is_termination_message(message: dict) -> bool:
    content = message.get("content")
    if content is None:
        return False

    return content.rstrip().endswith(TERMINATION_SYMBOL)
