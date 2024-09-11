from autogen import AssistantAgent, ConversableAgent


def is_termination_message(message: dict) -> bool:
    content = message.get("content")
    if content is None:
        return False

    content = str(content).strip().lower()
    return content in ["terminate", "end", "stop", "exit"]


def create_file_proxy(agent: ConversableAgent, trigger: ConversableAgent) -> ConversableAgent:
    proxy = ConversableAgent(
        name="Editor",
        system_message="A file editor to read and modify a file.",
        llm_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
        function_map={
            "save_file": None,
            "remove_content": None,
            "insert_content": None,
        },
        default_auto_reply="Keep going or exit the file by replying 'exit'.",
    )

    agent.register_nested_chats(
        chat_queue=[
            {
                "sender": proxy,
                "recipient": agent,
                "message": f"""\
You entered the file editor.

File Content
------------
{content}""",
            }
        ],
        trigger=trigger,
    )

    # TODO: Add tools to agents and remove after finishing the edit.

    return proxy


def create_editor_proxy(agent: ConversableAgent) -> ConversableAgent:
    proxy = ConversableAgent(
        name="Editor",
        system_message="A project editor to manage files and directories.",
        llm_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_message,
        function_map={
            "create_file": None,
            "create_dir": None,
            "list_dir": None,
            "show_dir_tree": None,
            "move_path": None,
            "delete_path": None,
            "enter_file": None,
        },
        default_auto_reply="Keep going or exit the editor by replying 'exit'.",
    )

    return proxy


def add_editing_capabilities(agent: AssistantAgent) -> AssistantAgent:
    editor = create_editor_proxy(agent)
    agent.add_conversable_agents([editor])

    return agent