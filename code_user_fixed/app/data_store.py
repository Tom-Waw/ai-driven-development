from typing import Dict
from app.models import User

users: Dict[int, User] = {}


def clear_users():
    global users
    users = {}

from app.models import Game

# Fixed list of games
GAMES = [
    Game(name="Pokebeasts", necessary_age=6),
    Game(name="Heat Age", necessary_age=6),
    Game(name="Call of War", necessary_age=18)
]