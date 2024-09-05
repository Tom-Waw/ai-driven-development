from prompts.template import Template

CODE_INDICATOR = "```code"
CODE_ORIGINAL = "<<<<< ORIGINAL"
CODE_SEPARATOR = "====="
CODE_MODIFIED = ">>>>> MODIFIED"
CODE_END = "```"


CodingTemplate = Template(
    f"""
{CODE_INDICATOR}
{{path}}
{CODE_ORIGINAL}
{{original_code}}
{CODE_SEPARATOR}
{{modified_code}}
{CODE_MODIFIED}
{CODE_END}
"""
)

CodingExample = CodingTemplate.render(
    path="src/main.py",
    original_code="def greeting():\n    print('Hello, World!')",
    modified_code="def greeting(name: str):\n    print(f'Hello, {{name}}!')",
)


CodingSystemPrompt = f"""
You have the ability to generate and persist code snippets for a code base.
Use the following template to indicate a coding attempt in your response:
{CodingTemplate}
For example:
{CodingExample}

The first match of the <original_code> will be replaced with the <modified_code>.
Only when using the template will the code be parsed and saved to the code base.
"""
