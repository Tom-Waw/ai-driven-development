CODE_INDICATOR = "```code"
CODE_ORIGINAL = "<<<<< ORIGINAL"
CODE_SEPARATOR = "====="
CODE_MODIFIED = ">>>>> MODIFIED"
CODE_END = "```"

CODING_TEMPLATE = f"""
{CODE_INDICATOR}
<file_name or path>
{CODE_ORIGINAL}
<original_code>
{CODE_SEPARATOR}
<modified_code>
{CODE_MODIFIED}
{CODE_END}
"""

CodingSystemPrompt = f"""
You have the ability to generate and persist code snippets for a code base.
Use the following template to indicate a coding attempt in your response:
{CODING_TEMPLATE}
For example:
{CODE_INDICATOR}
src/main.py
{CODE_ORIGINAL}
def greeting():
    print("Hello, World!")
{CODE_SEPARATOR}
def greeting(name: str):
    print(f"Hello, {{name}}!")
{CODE_MODIFIED}
{CODE_END}

The first match of the <original_code> will be replaced with the <modified_code>.
Only when using the template will the code be parsed and saved to the code base.
"""
