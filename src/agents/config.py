from autogen import config_list_from_json

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")

base_config = {
    "config_list": config_list,
    "cache_seed": None,
    "temperature": 0,
}

COMPLETION_PROMPT = """
    Do not show any appreciation in your responses.
    Reply APPROVED if you consider your task finished.
"""
