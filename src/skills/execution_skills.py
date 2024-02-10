import subprocess
from struct import pack
from typing import Annotated, Callable, List

from utils import safe_path


@safe_path(check_path=False)
def execute_python_script(path: Annotated[str, "Path of python script to execute"]) -> str:
    """Execute a python script"""
    with open(path, "r") as file:
        script = file.read()

    try:
        exec(script)
    except Exception as e:
        return f"Error: {e}"

    return "Script executed"


def list_python_packages() -> List[str]:
    """List all installed python packages by reading requirements-dev.txt."""
    with open("requirements-dev.txt", "r") as file:
        packages = file.readlines()

    # Remove the newline character from the end of each package
    return [package.strip() for package in packages]


def install_python_package(package: Annotated[str, "Name of the package to install"]) -> str:
    """Install a python package and add it to requirements-dev.txt."""
    try:
        # Check if the package is already installed
        packages = list_python_packages()
        if any(package in p for p in packages):
            return f"Package {package} is already installed"

        # Install the package
        subprocess.run(["pip", "install", package], check=True)

        # Add the package to requirements-dev.txt
        with open("requirements-dev.txt", "a") as file:
            file.write(f"{package}\n")

    except Exception as e:
        return f"Error: {e}"

    return f"Package {package} installed successfully"


def uninstall_python_package(package: Annotated[str, "Name of the package to uninstall"]) -> str:
    """Uninstall a python package and remove it from requirements-dev.txt."""
    try:
        # Check if the package is installed
        packages = list_python_packages()
        if all(package not in p for p in packages):
            return f"Package {package} is not installed"

        # Remove the package from the list
        packages.remove(package)

        # Write the list back to the file
        with open("requirements-dev.txt", "w") as file:
            file.write("\n".join(packages) + "\n")

        # Uninstall the package
        subprocess.run(["pip", "uninstall", package, "-y"], check=True)

    except Exception as e:
        return f"Error: {e}"

    return f"Package {package} uninstalled successfully"


execution_skills: list[tuple[Callable, str]] = [
    (execute_python_script, "Execute a python file. Can't be used with individual commands."),
    (list_python_packages, "List all installed python packages related to the task."),
    (install_python_package, "Install a python package."),
    (uninstall_python_package, "Uninstall a python package."),
]
