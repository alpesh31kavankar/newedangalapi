from pydantic import BaseModel
from datetime import datetime

class VoteBase(BaseModel):
    question_rounds_id: int
    products_id: int

class VoteCreate(VoteBase):
    """Data sent by frontend when casting a vote (no user_id)."""
    pass

class VoteOut(VoteBase):
    id: int
    users_id: int
    created_at: datetime

    class Config:
        orm_mode = True
