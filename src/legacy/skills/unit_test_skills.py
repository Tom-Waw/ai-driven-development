from typing import Annotated, List, Type
from unittest import TestLoader, TestResult

from settings import Settings
from skills.base import Skill, SkillSet
from skills.io_skills import SafePathSkill


class UnitTestSkill(SafePathSkill):
    description = "Run all tests inside a test script or directory relative to the test directory."

    def execute(self, path: Annotated[str, "Path for test discovery"]) -> str:
        """Run a test script"""
        full_path = self.validate_and_resolve_path(path)
        if not full_path.exists():
            raise ValueError(f"Path {path} does not exist")

        try:
            test_loader = TestLoader()
            test_suite = test_loader.discover(str(full_path))

            test_result = TestResult()
            test_suite.run(result=test_result)

            if test_result.wasSuccessful():
                return "All tests passed"

            return f"""
                Tests run: {test_result.testsRun},
                Failures: {len(test_result.failures)},
                Errors: {len(test_result.errors)}
            """
        except Exception as e:
            return f"Error: {e}"


class UnitTestSkillSet(SkillSet):
    def __init__(self) -> None:
        self.work_dir = Settings.TEST_DIR
        super().__init__()

    @property
    def skill_set(self):
        return [UnitTestSkill]

    def init_skills(self) -> List[Skill]:
        return [skill(work_dir=self.work_dir) for skill in self.skill_set]
