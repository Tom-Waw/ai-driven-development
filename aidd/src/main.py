import os
from datetime import datetime

from agency.implementation import init_developers, run_implementation
from agency.sprint_planning import init_planners, plan_sprint
from settings import reset, settings
from tee_logging import Tee

REQUEST = """\
# Projektbeschreibung: FastAPI-Anwendung mit CRUD-Funktionalitäten

## Projektziel

Das Ziel dieses Projekts ist die Entwicklung einer einfachen FastAPI-Anwendung,
die grundlegende CRUD-Operationen (Create, Read, Update, Delete) für eine Benutzerentität (User) bereitstellt.
Die Anwendung soll es ermöglichen, Benutzer zu erstellen, ihre Daten abzurufen, bestehende Benutzerinformationen zu aktualisieren und Benutzer zu löschen.

## Entität: User

Die zentrale Entität der Anwendung ist ein **User**, der durch folgende Attribute beschrieben wird:

- **ID**: Eine eindeutige ID, die automatisch generiert wird.
- **Name**: Der Name des Benutzers, als String.
- **Alter**: Das Alter des Benutzers, als Integer.

## Endpunkte

Die API soll die folgenden Endpunkte zur Verfügung stellen:

- **POST /users**: Erstellt einen neuen Benutzer mit Name und Alter und gibt die Benutzer-ID zurück.
- **GET /users/{user_id}**: Gibt die Details eines Benutzers basierend auf der Benutzer-ID zurück.
- **PUT /users/{user_id}**: Aktualisiert die Informationen eines Benutzers (Name und/oder Alter) basierend auf der Benutzer-ID.
- **DELETE /users/{user_id}**: Löscht einen Benutzer basierend auf der Benutzer-ID.

## Anforderungen

1. Die Anwendung muss in **Python** mit dem Framework **FastAPI** implementiert werden.
2. Es wird keine Datenbankanbindung verwendet. Stattdessen sollen die Daten temporär im Speicher (In-Memory) gehalten werden.
3. Die API soll in der Lage sein, HTTP-Requests zu verarbeiten und die entsprechenden JSON-Antworten zurückzugeben.
4. Eine einfache Fehlerbehandlung soll eingebaut werden, um sicherzustellen, dass nicht existierende Benutzer korrekt gehandhabt werden (z. B. durch Rückgabe eines 404-Fehlers).
"""


def main():
    reset()

    init_planners(request=REQUEST)
    init_developers(request=REQUEST)

    session_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = f"{settings.logfile}/{session_id}"
    os.makedirs(log_path, exist_ok=True)

    i = 0
    while True:
        log_path = f"{settings.logfile}/{session_id}/sprint_{i}"
        with Tee(f"{log_path}.planning.log"):
            sprint = plan_sprint(iteration=i)

        if sprint is None:
            # Project finished
            break

        with Tee(f"{log_path}.implementation.log"):
            run_implementation(sprint=sprint)

        print(
            f"""\
Sprint {i} finished.

{sprint.model_dump_json(indent=2)}"""
        )
        i += 1

    print("Project finished.")


if __name__ == "__main__":
    main()
