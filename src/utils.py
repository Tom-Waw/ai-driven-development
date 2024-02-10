import os
from functools import wraps

from settings import Settings


def clean_output_dir():
    """Clean the output directory."""
    import os
    import shutil

    if os.path.exists("output"):
        shutil.rmtree("output")

    os.makedirs("output")


@staticmethod
def safe_path(check_path=False):
    def decorator(method):
        @wraps(method)
        def wrapper(path, *args, **kwargs):
            abs_path = os.path.abspath(os.path.join(Settings.WORK_DIR, path))

            if check_path and not os.path.exists(abs_path):
                raise ValueError("File does not exist")

            if not os.path.commonpath([abs_path, Settings.WORK_DIR]) == Settings.WORK_DIR:
                raise ValueError("Access denied: Attempted access outside of working directory")

            if os.path.islink(abs_path):
                raise ValueError("Security alert: Path is a symbolic link")

            return method(abs_path, *args, **kwargs)

        return wrapper

    return decorator
