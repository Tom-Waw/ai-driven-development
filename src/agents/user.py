from autogen import UserProxyAgent


def is_termination_msg(msg):
    return "TERMINATE" in msg.get("content", "")


def create_user_proxy(llm_config=None, function_map=None) -> UserProxyAgent:
    USER_PROXY_PROMPT = (
        "A human admin. You are responsible for the final approval of the task. "
        + "Reply TERMINATE if the task has been solved at full satifaction and all agents succeeded with their responsibilty."
    )

    return UserProxyAgent(
        "user_proxy",
        system_message=USER_PROXY_PROMPT,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        code_execution_config=False,
        llm_config=llm_config,
        function_map=function_map,
    )
