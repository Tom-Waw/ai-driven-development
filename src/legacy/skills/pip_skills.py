import subprocess
from abc import ABC, abstractmethod
from typing import Annotated, List

from settings import Settings
from skills.base import Skill, SkillSet


class ListPackagesSkill(Skill):
    description = "List all installed python packages related to the task."

    def execute(self) -> List[str]:
        """List all installed python packages by reading requirements.txt."""
        return self.list_python_packages()

    @staticmethod
    def list_python_packages() -> List[str]:
        """List all installed python packages by reading requirements.txt."""
        with open(Settings.REQUIREMENTS_PATH, "r") as file:
            packages = file.readlines()

        # Remove the newline character from the end of each package
        return [package.strip() for package in packages]


class ManagePackageSkill(Skill, ABC):
    def execute(self, package: Annotated[str, "Name of the package"]) -> str:
        """Install or uninstall a python package and add or remove it from requirements.txt."""
        try:
            packages = ListPackagesSkill.list_python_packages()
            result = self.command(package, packages)

            # Write the list back to the file
            with open(Settings.REQUIREMENTS_PATH, "w") as file:
                file.write("\n".join(packages) + "\n")

        except Exception as e:
            return f"Error: {e}"

        return result

    @abstractmethod
    def command(self, package: str, packages: List[str]) -> str: ...


class InstallPackageSkill(ManagePackageSkill):
    description = "Install a python package and add it to requirements.txt."

    def command(self, package: str, packages: List[str]) -> str:
        """Install a python package and add it to the packages list."""
        # Check if the package is already installed
        if any(package in p for p in packages):
            return f"Package {package} is already installed"

        subprocess.run(["pip", "install", package], check=True)
        packages.append(package)

        return f"Package {package} installed successfully"


class UninstallPackageSkill(ManagePackageSkill):
    description = "Uninstall a python package and remove it from requirements.txt."

    def command(self, package: str, packages: List[str]) -> str:
        """Uninstall a python package and remove it from the packages list."""
        # Check if the package is installed
        if all(package not in p for p in packages):
            return f"Package {package} is not installed"

        subprocess.run(["pip", "uninstall", package, "-y"], check=True)
        packages.remove(package)

        return f"Package {package} uninstalled successfully"


class PipSkillSet(SkillSet):
    @property
    def skill_set(self) -> List[type[Skill]]:
        return [
            ListPackagesSkill,
            InstallPackageSkill,
            UninstallPackageSkill,
        ]
