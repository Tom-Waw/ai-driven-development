from abc import ABC, abstractmethod
from functools import wraps

from autogen import ConversableAgent, agentchat
from typing_extensions import Self


class Skill(ABC):
    description: str = NotImplemented

    @abstractmethod
    def execute(self, *args, **kwargs): ...

    def register_agents(self, caller: ConversableAgent, executor: ConversableAgent) -> None:
        @wraps(self.execute)
        def proxy(*args, **kwargs):
            return self.execute(*args, **kwargs)

        agentchat.register_function(
            proxy,
            caller=caller,
            executor=executor,
            description=self.description,
        )


class SkillSet(ABC):
    def __init__(self) -> None:
        self.skills = self.init_skills()

    @property
    @abstractmethod
    def skill_set(self) -> list[type[Skill]]: ...

    def init_skills(self) -> list[Skill]:
        return [skill() for skill in self.skill_set]

    @classmethod
    def register(cls, *args, caller: ConversableAgent, executor: ConversableAgent, **kwargs) -> Self:
        skill_set = cls(*args, **kwargs)
        skill_set.register_all(caller, executor)
        return skill_set

    def register_all(self, caller: ConversableAgent, executor: ConversableAgent) -> None:
        for skill in self.skills:
            skill.register_agents(caller, executor)
