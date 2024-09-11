import shutil

from git import Repo
from settings import settings
# from state.project_state import ProjectState

# project_state: ProjectState = None
# repo: Repo = None


# def reset(client_request: str):
def reset() -> Repo:
    # global project_state, repo

    # Reset the project state
    # project_state = ProjectState(client_request=client_request)

    # Reset the project directory
    for item in settings.project_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    shutil.copytree(settings.template_dir, settings.project_dir, dirs_exist_ok=True)

    # Initialize the git repository
    repo = Repo.init(settings.project_dir, initial_branch=settings.main_branch)
    repo.index.add(["."])
    repo.index.commit("Initial commit")

    print("Project reset.")
    return repo
