from fastapi import FastAPI
from app.routers import game

app = FastAPI(
    title="Dev Mind Speed Game API",
    version="1.0"
)

app.include_router(game.router, prefix="/game")

