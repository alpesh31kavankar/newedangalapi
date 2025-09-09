from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DrawBase(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    result_time: datetime
    is_active: Optional[bool] = True

class DrawCreate(DrawBase):
    pass

class DrawUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result_time: Optional[datetime] = None
    is_active: Optional[bool] = None

class DrawOut(DrawBase):
    draw_id: int

    class Config:
        orm_mode = True
