# app/schemas/spin_schema.py
from pydantic import BaseModel
from datetime import datetime

# Request model
class SpinRequest(BaseModel):
    prize_type: str
    prize_value: int = 0


# Response model for history
class SpinHistoryOut(BaseModel):
    id: int
    user_id: int
    prize_type: str
    prize_value: int
    created_at: datetime

    class Config:
        orm_mode = True
