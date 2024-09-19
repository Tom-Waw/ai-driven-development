from agency.implementation import init_developers, run_implementation
from agency.sprint_planning import init_planners, plan_sprint
from settings import reset

REQUEST = """\
The project is a Python application built with FastAPI that provides an API for users to send JSON data.
When data is submitted, it is stored in a text file, and the API responds with an ID corresponding to the entry.
The application includes all standard CRUD operations, allowing users to create new entries,
retrieve data by ID, update existing entries, and delete entries.
Data management is handled through basic file operations on the text file storing the JSON entries."""


def main():
    reset()

    init_planners(request=REQUEST)
    init_developers(request=REQUEST)

    for i in range(5):
        sprint = plan_sprint(iteration=i)
        if sprint is None:
            # Project finished
            break

        run_implementation(sprint=sprint)

        print(
            f"""\
Sprint {i} finished.

{sprint.model_dump_json(indent=2)}"""
        )

    print("Project finished.")


if __name__ == "__main__":
    main()
