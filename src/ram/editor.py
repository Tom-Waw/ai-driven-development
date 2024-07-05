from pathlib import Path

from pydantic import BaseModel

from utils import dir_tree


class Editor(BaseModel):
    workdir: Path = Path("/app")

    def __str__(self):
        # Show the file structure of the working directory
        tree = dir_tree(self.workdir)
        return "\n".join(tree)

    def validate_rel_path(self, rel_path: str) -> Path:
        full_path = self.workdir / rel_path

        if not full_path.is_relative_to(self.workdir):
            raise ValueError(f"Access denied: Attempted access outside of working directory at path: {rel_path}")

        if full_path.is_symlink():
            raise ValueError(f"Security alert: Path is a symbolic link at path: {rel_path}")

        return full_path
