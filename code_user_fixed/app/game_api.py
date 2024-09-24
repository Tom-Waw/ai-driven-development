from app.data_store import GAMES, users
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/can_play")
def can_play(user_id: int, game_name: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user = users[user_id]
    game = next((game for game in GAMES if game.name == game_name), None)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if user.age >= game.necessary_age:
        return {"can_play": True}
    return {"can_play": False}
