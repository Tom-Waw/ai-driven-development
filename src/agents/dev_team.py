from autogen import AssistantAgent

from agents.team import Team

from .config import base_config

SW_ARCHITECT_PROMPT = (
    "Software Architect, creative and experienced in designing and planning software systems. "
    + "You create a layout and concept of the software. You review the code base and provide feedback to the developer. "
)
DEVELOPER_PROMPT = (
    "A Software Developer specialized in python. You follow an approved plan and implement the code. "
    + "Generate the python code based on the requirements provided."
)
TESTER_PROMPT = "A Tester. Test and review the code and provide feedback to the team."


class DevTeam(Team):

    @classmethod
    def build_agents(cls, llm_config=base_config):
        agents = super().build_agents(cls.io_adapter, llm_config)

        software_architect = AssistantAgent(
            "software_architect",
            system_message=SW_ARCHITECT_PROMPT,
            llm_config=llm_config,
        )

        developer = AssistantAgent(
            "developer",
            system_message=DEVELOPER_PROMPT,
            llm_config={
                **llm_config,
                "functions": cls.io_adapter.function_configs,
            },
            function_map=cls.io_adapter.function_map,
        )

        tester = AssistantAgent(
            "tester",
            system_message="A Tester. You implement and test the code and provide feedback to the developer.",
            code_execution_config=False,
            llm_config={
                **llm_config,
                "functions": cls.io_adapter.function_configs,
            },
            function_map=cls.io_adapter.function_map,
        )

        return agents + [software_architect, developer, tester]
