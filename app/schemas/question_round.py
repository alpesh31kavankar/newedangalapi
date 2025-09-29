from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QuestionRoundBase(BaseModel):
    questions_id: int
    categories_id: int
    product1_id: int
    product2_id: int
    release_time: datetime
    max_votes: int

class QuestionRoundCreate(QuestionRoundBase):
    pass

class QuestionRoundOut(QuestionRoundBase):
    id: int
    is_locked: bool
    votes_product1: int
    votes_product2: int
    winner_product_id: Optional[int]
    is_draw: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
