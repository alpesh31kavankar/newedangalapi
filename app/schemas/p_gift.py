from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PGiftBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    quantity: int = 1
    price: int = 0
    status: str = 'inactive'

class PGiftCreate(PGiftBase):
    pass

class PGiftUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[int] = None
    status: Optional[str] = None

class PGiftOut(PGiftBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
