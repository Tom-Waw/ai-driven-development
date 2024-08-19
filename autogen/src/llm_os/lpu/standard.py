import os

config_list = [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]
# config_list_claude = [
#     {
#         "model": "claude-3-5-sonnet-20240620",
#         "api_key": os.getenv("ANTHROPIC_API_KEY"),
#         "api_type": "anthropic",
#     }
# ]


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
