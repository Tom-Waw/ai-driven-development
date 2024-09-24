from app.data_store import users
from app.models import User
from fastapi import APIRouter

router = APIRouter()


@router.post("/users")
def create_user(user: User):
    user_id = len(users) + 1
    users[user_id] = user
    return {"user_id": user_id}


@router.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id in users:
        return users[user_id].model_dump()
    return {"error": "User not found"}, 404


@router.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    if user_id in users:
        users[user_id].update(user.model_dump())
        return users[user_id]
    return {"error": "User not found"}, 404


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id in users:
        del users[user_id]
        return {"message": "User deleted successfully"}, 200
    return {"error": "User not found"}, 404