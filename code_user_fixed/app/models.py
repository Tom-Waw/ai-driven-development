from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


class Game(BaseModel):
    name: str
    necessary_age: int