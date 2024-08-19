from agents import create_assistant
from llm_os.tooling.editor_tools import editor_tool_registry

import autogen

SYSTEM_MESSAGE = """
You are a well trained professional software developer (python).
Only terminate after reconfirming the files and directories you have created.
"""


def get_assistant(proxy: autogen.UserProxyAgent, system_message: str = SYSTEM_MESSAGE):
    assistant = create_assistant("Assistant", system_message=system_message)
    editor_tool_registry.assign(proxy, assistant)
    return assistant
