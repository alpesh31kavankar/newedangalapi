from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------- Shared Base ----------
class GiftBase(BaseModel):
    name: str = Field(..., description="Name of the gift item")
    description: Optional[str] = Field(None, description="Details about the gift")
    image_url: Optional[str] = Field(None, description="URL of the gift image")
    quantity: int = Field(1, description="Number of items available")
    price: int = Field(0, description="Price or value of the gift")
    status: str = Field('inactive', description="Status of the gift (active/inactive)")


# ---------- Create ----------
class GiftCreate(GiftBase):
    pass


# ---------- Update ----------
class GiftUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[int] = None
    status: Optional[str] = None


# ---------- Response ----------
class GiftOut(GiftBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
