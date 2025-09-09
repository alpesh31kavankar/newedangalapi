from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserTokenSummaryBase(BaseModel):
    user_id: int
    draw_id: int
    total_participant_tokens: Optional[int] = 0
    total_winning_tokens: Optional[int] = 0

class UserTokenSummaryCreate(UserTokenSummaryBase):
    pass

class UserTokenSummaryUpdate(BaseModel):
    total_participant_tokens: Optional[int]
    total_winning_tokens: Optional[int]

class UserTokenSummaryOut(UserTokenSummaryBase):
    summary_id: int
    updated_at: datetime

    class Config:
        orm_mode = True
