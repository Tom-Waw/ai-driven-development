from textwrap import dedent

from crewai import Agent, Crew, Task

from .management import software_engineer

### Agents ###

developer = Agent(
    role="Developer",
    goal="Work on the ticket assigned to you.",
    backstory=dedent(
        """\
        You are a senior developer at a leading software company.
        You are responsible for developing high-quality software applications.
        You have experience working on various projects and technologies and do your best to deliver perfect code.
        """
    ),
    allow_delegation=False,
)

### Tasks ###

implementation_task = Task(
    agent=developer,
    description=dedent(
        """\
        Given the project information and the ticket, work on the project until the ticket is done.

        Project Information
        -------------------
        {project_info}

        Ticket
        ------
        {ticket}
        """
    ),
    expected_output="The full python code for the prototype. Nothing else.",
)

### Crew ###

dev_crew = Crew(
    agents=[developer, software_engineer],
    tasks=[implementation_task],
    planning=True,
    verbose=True,
)
