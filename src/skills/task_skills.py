from enum import Enum

from autogen import ConversableAgent
from pydantic import BaseModel


class TaskStatus(str, Enum):
    TODO = "todo"
    TEST_PHASE = "test_phase"
    IMPLEMENTATION_PHASE = "implementation_phase"
    REVIEW_PHASE = "review_phase"
    DONE = "done"


class Task(BaseModel):
    name: str
    description: str
    priority: int = 0
    status: TaskStatus = TaskStatus.TODO
    assignee: ConversableAgent | None = None


class Project(BaseModel):
    name: str
    description: str
    backlog: list[Task] = []
    sprint: list[Task] = []
    done: list[Task] = []
