from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserAdBase(BaseModel):
    user_id: int
    rewarded_token: Optional[bool] = False
    next_available_at: Optional[datetime] = None

class UserAdCreate(UserAdBase):
    pass

class UserAdOut(UserAdBase):
    ad_id: int
    watched_at: datetime

    class Config:
        orm_mode = True
