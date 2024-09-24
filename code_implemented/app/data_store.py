from typing import Dict

users: Dict[int, Dict[str, str]] = {}


def clear_users():
    global users
    users = {}
