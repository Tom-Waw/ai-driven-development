import shutil

from ram.editor import Editor
from ram.ticket_system import TicketSystem
from settings import settings

editor = Editor()
ticket_system = TicketSystem()


def reset():
    for path in settings.project_dir.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    # Copy from settings.templates_dir to settings.project_dir
    shutil.copytree(settings.template_dir, settings.project_dir, dirs_exist_ok=True)
    print("Project directory reset.")
