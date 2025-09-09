from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional

class UserTokenBase(BaseModel):
    user_id: int
    draw_id: int
    unlock_id: Optional[int]
    token_type: Literal['participant', 'winning']

class UserTokenCreate(UserTokenBase):
    pass

class UserTokenOut(UserTokenBase):
    token_id: int
    issued_at: datetime

    class Config:
        orm_mode = True
