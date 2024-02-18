from typing import Annotated
from unittest import TestLoader, TestResult

from settings import Settings
from skills.io_skills import CodingSkillSet, SafePathSkill


class UnitTestSkill(SafePathSkill):
    description = "Run all tests inside a test script or directory."
    raise_on_404 = True

    def execute(self, path: Annotated[str, "Path for test discovery"]) -> str:
        """Run a test script"""
        try:
            test_loader = TestLoader()
            test_suite = test_loader.discover(path)

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


class UnitTestSkillSet(CodingSkillSet):
    def __init__(self) -> None:
        super().__init__(work_dir=Settings.TEST_DIR)

    @property
    def skill_set(self):
        return super().skill_set + [UnitTestSkill]
