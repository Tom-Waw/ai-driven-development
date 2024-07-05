import shutil

from ram.editor import Editor
from ram.ticket_system import TicketSystem

ticket_system = TicketSystem()
editor = Editor()


def reset():
    if editor.workdir.exists():
        for item in editor.workdir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    editor.workdir.mkdir(parents=True, exist_ok=True)


def show():
    pretty_repr = "\n".join(
        (
            "Project:",
            ticket_system.model_dump_json(indent=4),
            "----------------\n",
            "Session:",
            str(editor),
        )
    )

    print(pretty_repr)
