from textwrap import dedent

from agency.tools.editor import (
    CreateDir,
    CreateFile,
    DeletePath,
    ListDir,
    MovePath,
    ReadFile,
    ShowDirTree,
    WriteContent,
)
from crewai import Agent

software_architect = Agent(
    role="Software Architect",
    goal="Oversee the development process to ensure the code quality and project success.",
    backstory=dedent(
        """\
        A software architect at a leading software company.
        Given any kind of project idea, is able to:
        - understand the requirements
        - foresee potential issues
        - come up with the ideal project structure
        - map out the next logical steps of the development process
        - write concise and clear tickets for the developers
        """
    ),
)

coder = Agent(
    role="Developer",
    goal="Work on the ticket assigned to you.",
    backstory=dedent(
        """\
        An experienced developer at a leading software company, responsible for implementing high-quality software applications.
        Always delivers clean, maintainable code that meets the requirements.
        """
    ),
    tools=[
        CreateDir(),
        CreateFile(),
        ListDir(),
        ShowDirTree(),
        ReadFile(),
        WriteContent(),
        MovePath(),
        DeletePath(),
    ],
)
