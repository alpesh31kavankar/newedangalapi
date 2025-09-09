from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionUnlockBase(BaseModel):
    draw_id: int
    category_id: int
    question_id: int
    product1_id: int
    product2_id: int
    unlock_time: datetime
    cutoff_time: datetime
    max_users: int = 100

class QuestionUnlockCreate(QuestionUnlockBase):
    pass

class QuestionUnlockOut(QuestionUnlockBase):
    unlock_id: int
    current_users: int
    is_closed: bool
    processed: bool
    winning_product_id: Optional[int]

    class Config:
        orm_mode = True
