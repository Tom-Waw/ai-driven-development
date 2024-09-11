import state
from crewai_tools import BaseTool
from git import Repo

# class GetProjectState(BaseTool):
#     name: str = "Get Project State Tool"
#     description: str = "Get the meta information about the project and former sprints."

#     def _run(self) -> str:
#         return state.project_state.model_dump_json(indent=4, exclude="current_sprint")


# class GetSprint(BaseTool):
#     name: str = "Get Sprint Tool"
#     description: str = "Get an overview of the current sprint. Use this to see the progress of the tickets."

#     def _run(self) -> str:
#         if state.project_state.current_sprint is None:
#             return "No active sprint."

#         return state.project_state.current_sprint.model_dump_json(indent=4)


# class CommitChanges(BaseTool):
#     name: str = "Commit Changes Tool"
#     description: str = "Commit changes in the working directory."

#     def _run(self, message: str) -> str:
#         state.repo.index.add(["."])
#         state.repo.index.commit(message)
#         return f"Changes committed."


class ShowDiff(BaseTool):
    name: str = "Sprint Changes Tool"
    description: str = "Shows the differences of the project before and after the current sprint."

    def __init__(self, repo: Repo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._repo = repo

    def _run(self) -> str:
        return str(self._repo.index.diff(None))
