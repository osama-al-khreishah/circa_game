from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URL)

db = client["circa_game_db"]

games_collection = db["games"]