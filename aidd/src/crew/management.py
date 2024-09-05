from textwrap import dedent

from crewai import Agent, Crew, Process, Task
from state.project_state import ProjectStateInit
from state.sprint import Sprint

### Agents ###

software_engineer = Agent(
    role="Software Engineer",
    goal="Oversee the development process to ensure the code quality and project success.",
    backstory=dedent(
        """\
        You are a software engineer at a leading software company.
        Given any kind of project idea, you are able to:
        - understand the requirements
        - foresee potential issues
        - come up with the ideal code architecture and best practices
        - map out the development process
        - give perfect instructions to the developers via tickets
        """
    ),
    allow_delegation=False,
)


### Tasks ###


kickoff_task = Task(
    agent=software_engineer,
    description=dedent(
        """\
        Based on the client request, initialize the project.
        Define the project goal and extract the requirements the project needs to fulfill.

        Client Request
        --------------
        {client_request}
        """
    ),
    expected_output="The project state initialization.",
    output_pydantic=ProjectStateInit,
)


sprint_planning_task = Task(
    agent=software_engineer,
    description=dedent(
        """\
        Given the project goal, requirements and the results of former sprints, plan the next sprint.
        Given these insights, think about the next goal your team needs to achieve.

        With that goal in mind, create tickets for the developers to accomplish said goal.

        Project Insights
        -----------------
        {insights}
        """
    ),
    expected_output="The plan for the next sprint.",
    output_pydantic=Sprint,
)

### Crews ###

kickoff_crew = Crew(
    agents=[software_engineer],
    tasks=[kickoff_task],
    process=Process.sequential,
    verbose=True,
)

sprint_planning_crew = Crew(
    agents=[software_engineer],
    tasks=[sprint_planning_task],
    process=Process.sequential,
    planning=True,
    verbose=True,
)
