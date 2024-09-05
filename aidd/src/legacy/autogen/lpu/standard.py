import os

MODEL = "gpt-4o-mini"
config_list = [
    {
        "model": MODEL,
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
]


base_config = {
    "config_list": config_list,
    "cache_seed": None,
    "temperature": 0,
}


TERMINATION_SYMBOL = "TERMINATE"

APPRECIATION_CONSTRAINT = "\nDo not show any appreciation in your responses."
END_CONVERSATION = f"\nReply '{TERMINATION_SYMBOL}' if the task has been solved at full satisfaction."


def is_termination_message(message: dict) -> bool:
    content = message.get("content")

    if content is None:
        return False

    return TERMINATION_SYMBOL in content
