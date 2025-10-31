from pydantic import BaseModel

class AnswerCreate(BaseModel):
    user_id: int
    answer: str  # 'Yes' or 'No'

class AnswerResult(BaseModel):
    yes_count: int
    no_count: int
