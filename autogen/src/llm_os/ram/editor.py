from functools import wraps
from pathlib import Path

from llm_os.ram.utils import dir_tree
from pydantic import BaseModel


# Decorator to validate the path
def valid_path(func):
    @wraps(func)
    def wrapper(self: "Editor", path: str, *args, **kwargs):
        full_path = self.workdir / path

        if not full_path.is_relative_to(self.workdir):
            raise ValueError(f"Access denied: Attempted access outside of working directory at path: {path}")

        if full_path.is_symlink():
            raise ValueError(f"Security alert: Path is a symbolic link at path: {path}")

        return func(self, full_path, *args, **kwargs)

    wrapper.__annotations__["path"] = str
    return wrapper


class Editor(BaseModel):
    workdir: Path = Path("/code")

    ### CREATE ###

    @valid_path
    def create_dir(self, path: Path) -> None:
        """Create a directory in the working directory."""
        path.mkdir(parents=True)

    @valid_path
    def create_file(self, path: Path) -> None:
        """Create a file in the working directory."""
        path.touch()

    ### READ ###

    @valid_path
    def show_dir_tree(self, path: Path | None = None) -> str:
        """Shows a tree representation of a directory in the working directory."""
        tree = dir_tree(path or self.workdir)
        return "\n".join(tree)

    @valid_path
    def list_dir(self, path: Path | None = None) -> str:
        """List the content of a directory in the working directory."""
        path = path or self.workdir
        return "\n".join([p.name for p in path.iterdir()])

    @valid_path
    def read_file(self, path: Path) -> str:
        """Read the content of a file in the working directory."""
        with open(path, "r") as file:
            content = file.read()

        return content

    ### UPDATE ###

    @valid_path
    def overwrite_content(self, path: Path, overwrite_content: str, new_content: str) -> None:
        """Modify the content of a file in the working directory."""
        with open(path, "r") as file:
            old_content = file.read()

        content = old_content.replace(overwrite_content, new_content)

        if content == old_content:
            raise ValueError(f"Content '{overwrite_content}' not found in file at path: {path}")

        with open(path, "w") as file:
            file.write(content)

    ### DELETE ###

    @valid_path
    def delete(self, path: Path) -> None:
        """Delete a file or directory in the working directory."""
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()
