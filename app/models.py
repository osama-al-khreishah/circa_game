from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class StartGameRequest(BaseModel):    
    name: str
    difficulty: int = Field(..., ge=1, le=4)

class SubmitAnswerRequest(BaseModel):
    
    answer: float

class QuestionData(BaseModel):

    question: str
    answer: float
    submitted_answer: Optional[float] = None
    time_taken: Optional[float] = None

class GameData(BaseModel):

    game_id: UUID
    name: str
    difficulty: int
    time_started: datetime
    time_finished: Optional[datetime] = None
    questions: List[QuestionData] = []