from textwrap import dedent

from crewai_tools import BaseTool


class GetProjectState(BaseTool):
    name: str = "Get Project State Tool"
    description: str = "Get the meta information about the project and former sprints."

    def _run(self) -> str:
        # Load project state
        from state import project_state

        if project_state is None:
            return "The project has not been initialized yet."

        return dedent(
            f"""
            Project State:
            {project_state.model_dump_json(indent=4, exclude="current_sprint")}
            """
        )
