from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from uuid import uuid4
from datetime import datetime
from app.models import *
from app.questions import *
from app.database import *

router = APIRouter()    

@router.post("/start")
def start_game(payload : StartGameRequest):
    question_text, answer = generate_question(payload.difficulty)
    game_id = str(uuid4())

    question_obj = {
        "question": question_text,
        "answer": answer,
        "submitted_answer": None,
        "time_taken": None
    }

    # Create game object
    game = {
        "_id": game_id,
        "name": payload.name,
        "difficulty": payload.difficulty,
        "time_started": datetime.utcnow(),
        "time_ended": None,
        "questions": [question_obj]
    }

    # Insert into MongoDB
    games_collection.insert_one(game)

    return {
        "message": f"Hello {payload.name}, find your submit API URL below",
        "submit_url": f"/game/{game_id}/submit",
        "question": question_text,
        "time_started": game["time_started"]
    }

@router.post("/{game_id}/submit")
def submit_answer(game_id: str, payload: SubmitAnswerRequest):
    # Fetch game from DB
    game = games_collection.find_one({"_id": game_id})

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game["time_ended"] is not None:
        raise HTTPException(status_code=400, detail="This game has already ended")

    # Find last unanswered question
    questions = game["questions"]
    last_question = None
    for q in reversed(questions):
        if q["submitted_answer"] is None:
            last_question = q
            break

    if last_question is None:
        raise HTTPException(status_code=400, detail="No unanswered question found")

    # Time calculation
    now = datetime.utcnow()

    # Find time of last answered question or game start
    last_time = game["time_started"]
    for q in reversed(questions):
        if q.get("time_taken") is not None:
            last_time = last_time + timedelta(seconds=q["time_taken"])

    time_taken = round((now - last_time).total_seconds(), 2)

    # Check correctness
    is_correct = abs(payload.answer - last_question["answer"]) < 0.01

    # Update current question
    games_collection.update_one(
        {"_id": game_id, "questions.question": last_question["question"]},
        {
            "$set": {
                "questions.$.submitted_answer": payload.answer,
                "questions.$.time_taken": time_taken
            }
        }
    )

    # Generate next question
    new_question_text, new_answer = generate_question(game["difficulty"])
    new_question = {
        "question": new_question_text,
        "answer": new_answer,
        "submitted_answer": None,
        "time_taken": None
    }

    games_collection.update_one(
        {"_id": game_id},
        {"$push": {"questions": new_question}}
    )

    # Calculate score
    total_attempted = sum(1 for q in questions if q["submitted_answer"] is not None) + 1
    total_correct = sum(
        1 for q in questions if q.get("submitted_answer") is not None and
        abs(q.get("submitted_answer") - q.get("answer")) < 0.01
    ) + (1 if is_correct else 0)

    return {
        "result": (
            f"Good job {game['name']}, your answer is correct!" if is_correct
            else f"Sorry {game['name']}, your answer is incorrect."
        ),
        "time_taken": time_taken,
        "next_question": {
            "submit_url": f"/game/{game_id}/submit",
            "question": new_question_text
        },
        "current_score": f"{total_correct} / {total_attempted}"
    }
@router.get("/{game_id}/end")
def end_game(game_id: str):
    game = games_collection.find_one({"_id": game_id})

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game["time_ended"] is not None:
        return {"message": "Game already ended"}

    # End the game
    games_collection.update_one(
        {"_id": game_id},
        {"$set": {"time_ended": datetime.utcnow()}}
    )

    # Sum final score
    questions = game["questions"]
    total_questions = len(questions)
    correct_answers = sum(
        1 for q in questions if q.get("submitted_answer") is not None and
        abs(q["submitted_answer"] - q["answer"]) < 0.01
    )

    # Calculate all the time spended
    total_time = sum(q["time_taken"] for q in questions if q.get("time_taken") is not None)

    # Find best (The least time spended) question
    best_q = None
    min_time = float('inf')
    for q in questions:
        if q.get("time_taken") and q["time_taken"] < min_time:
            best_q = q
            min_time = q["time_taken"]

    return JSONResponse({
        "name": game["name"],
        "difficulty": game["difficulty"],
        "current_score": f"{correct_answers} / {total_questions}",
        "total_time_spent": total_time,
        "best_score": {
            "question": best_q["question"] if best_q else None,
            "answer": best_q["answer"] if best_q else None,
            "time_taken": best_q["time_taken"] if best_q else None
        },
        "history": questions
    })