import tempfile
from pathlib import Path

from settings import settings


class Editor:
    def __init__(self, path: Path = settings.project_dir):
        self.workspace = path
        self.session: Path | None = None

    def start_session(self):
        self.session = tempfile.TemporaryDirectory()


# class File(BaseModel):
#     """A file that contains text."""

#     name: str
#     content: str = Field("", exclude=True)


# class Directory(BaseModel):
#     """A directory that contains files and other directories."""

#     name: str
#     children: list[Self | File] = []


# class Editor:
#     """A class based editor with a workspace. Capable of editing and saving files and directories."""

#     def __init__(self, path: Path = settings.project_dir):
#         self.workspace: Directory
#         self.load_from_disk(path=path)

#     def save_to_disk(self):
#         """Writes the workspace to disk."""
#         settings.project_dir.mkdir(exist_ok=True)

#         self.recursive_save(self.workspace, settings.project_dir)

#     def recursive_save(self, directory: Directory, path: Path):
#         """Recursively saves the directory to disk."""
#         for item in directory.children:
#             if isinstance(item, File):
#                 fpath = path / f"{item.name}"
#                 fpath.write_text(item.content)
#             elif isinstance(item, Directory):
#                 new_path = path / item.name
#                 new_path.mkdir(exist_ok=True)
#                 self.recursive_save(item, new_path)

#     def load_from_disk(self, path: Path = settings.project_dir):
#         """Reads the workspace from disk."""
#         self.workspace = self.recursive_load(path)

#     def recursive_load(self, path: Path) -> Directory:
#         """Recursively loads the directory from disk."""
#         items = []

#         for child in path.iterdir():
#             if child.is_dir():
#                 item = self.recursive_load(child)
#                 items.append(item)
#             else:
#                 items.append(
#                     File(
#                         name=child.name,
#                         content=child.read_text(),
#                     )
#                 )

#         return Directory(name=path.name, children=items)

#     def reset(self):
#         """Resets the workspace."""
#         self.workspace.children.clear()
#         self.save_to_disk()
