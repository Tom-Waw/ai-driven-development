from typing import Annotated

from settings import Settings


def document_requirements(
    content: Annotated[str, "Content of the requirements documentation."],
) -> str:
    """Overwrites the requirements documentation markdown file."""
    with open(Settings.DOCU_PATH, "w") as file:
        file.write(content)

    return "Written to the requirements documentation file."
