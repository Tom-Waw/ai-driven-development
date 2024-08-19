from enum import Enum
from pathlib import Path
from typing import Generator, List, Tuple


def format_lines(lines: List[Tuple[int, str]]) -> str:
    """Format lines with line numbers."""
    return "".join([f"{i+1: >4}:{line}" for i, line in lines])


class DirTreePrefix(str, Enum):
    SPACE = "    "
    BRANCH = "│   "
    # pointers:
    TEE = "├── "
    LAST = "└── "


def dir_tree(path: Path, prefix: str = "") -> Generator[str, None, None]:
    if prefix == "":
        yield f"{path.name}/"

    contents = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    pointers = [DirTreePrefix.TEE] * (len(contents) - 1) + [DirTreePrefix.LAST]
    for pointer, subpath in zip(pointers, contents):
        yield f"{prefix}{pointer}{subpath.name}" + ("/" if subpath.is_dir() else "")

        if subpath.is_dir():
            extension = DirTreePrefix.BRANCH if pointer == DirTreePrefix.TEE else DirTreePrefix.SPACE
            yield from dir_tree(subpath, prefix=prefix + extension)
