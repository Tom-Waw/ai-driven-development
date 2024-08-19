import re

from lpu.parsing.abc import ResponseParser, Trigger

CODE_ORIGINAL = re.escape("<<<<< ORIGINAL")
CODE_SEPARATOR = re.escape("=====")
CODE_MODIFIED = re.escape(">>>>> MODIFIED")

CODING_FORMAT = f"""
<file_name>
{CODE_ORIGINAL}
<original_code>
{CODE_SEPARATOR}
<modified_code>
{CODE_MODIFIED}
"""

CODING_PATTERN = rf"""
    ([^\n]+)                    # File name
    \s*\n+{CODE_ORIGINAL}\s*\n
    (.*?)                       # Original code
    \s*\n{CODE_SEPARATOR}\s*\n
    (.*?)                       # Modified code
    \s*\n{CODE_MODIFIED}
"""


class CodingTrigger(Trigger):
    """A coding call with original and modified code."""

    file_name: str
    original_code: str
    modified_code: str


class CodingParser(ResponseParser):
    """Parser for coding responses."""

    @property
    def description(self) -> str:
        return (
            f"To indicate a coding attempt in your resonse, use the following format:{CODING_FORMAT}"
            + "For example:\n"
            + "".join(examples)
        )

    @property
    def response_field(self) -> str:
        return "coding"

    def parse(self, response: str, context: dict) -> None:
        """Parse a coding response from a string."""
        result = []
        for match in re.finditer(CODING_PATTERN, response, re.DOTALL | re.VERBOSE):
            # Extract the file name and the original and modified code
            file_name, original_code, modified_code = match
            result.append(
                CodingTrigger(
                    pos=match.pos,
                    file_name=file_name.strip(),
                    original_code=original_code,
                    modified_code=modified_code,
                )
            )

        # Add the coding response to the context
        if self.response_field not in context:
            context[self.response_field] = []
        context[self.response_field].append(result)


example_1 = f"""
Base Example:
demo.py
{CODE_ORIGINAL}
def greeting():
    print("Hello, World!")
{CODE_SEPARATOR}
def greeting(name: str):
    print(f"Hello, {{name}}!")
{CODE_MODIFIED}
"""

example_2 = f"""
Multiple Files Example:
demo.py
{CODE_ORIGINAL}
def greeting():
    print("Hello, World!")
{CODE_SEPARATOR}
def greeting(name: str):
    print(f"Hello, {{name}}!")
{CODE_MODIFIED}

tests/test_demo.py
{CODE_ORIGINAL}
def test_greeting():
    assert greeting() == "Hello, World!"
{CODE_SEPARATOR}
def test_greeting():
    assert greeting("Alice") == "Hello, Alice!"
{CODE_MODIFIED}
"""

examples = [example_1, example_2]
