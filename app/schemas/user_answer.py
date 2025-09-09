from pydantic import BaseModel
from datetime import datetime

class UserAnswerBase(BaseModel):
    unlock_id: int
    user_id: int
    chosen_product_id: int

class UserAnswerCreate(UserAnswerBase):
    pass

class UserAnswerOut(UserAnswerBase):
    answer_id: int
    answered_at: datetime

    class Config:
        orm_mode = True
