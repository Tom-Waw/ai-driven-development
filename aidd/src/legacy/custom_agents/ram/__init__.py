import shutil

from settings import settings


def reset():
    """Reset the project."""

    # Remove all the files and directories in the project directory
    for item in settings.project_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    shutil.copytree(
        settings.project_skeleton_dir,
        settings.project_dir,
        dirs_exist_ok=True,
    )