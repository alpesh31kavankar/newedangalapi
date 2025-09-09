# app/schemas/gift.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GiftBase(BaseModel):
    draw_id: int
    gift_type: str = Field(..., pattern="^(participant|winning)$")
    gift_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    quantity: int = 1
    is_active: bool = True

class GiftCreate(GiftBase):
    pass

class GiftUpdate(BaseModel):
    gift_name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = None

class GiftOut(GiftBase):
    gift_id: int
    created_at: datetime

    class Config:
        orm_mode = True
