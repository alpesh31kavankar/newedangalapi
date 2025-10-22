from pydantic import BaseModel
from datetime import datetime


class UserInfo(BaseModel):
    id: int
    username: str
    profile_image: str | None

    class Config:
        orm_mode = True
        
class LeaderboardBase(BaseModel):
    user_id: int
    month: str
    score: float

class LeaderboardCreate(LeaderboardBase):
    pass

class LeaderboardResponse(LeaderboardBase):
    id: int
    rank: int | None
    claimed: bool
    updated_at: datetime
    user: UserInfo 

    class Config:
        orm_mode = True
