# schemas/main_category.py
from pydantic import BaseModel, AnyUrl, Field
from typing import Optional
from datetime import datetime

class MainCategoryBase(BaseModel):
    name: str = Field(..., example="Sports")
    interval_minutes: Optional[int] = Field(10, example=15)
    image_url: Optional[str] = Field(None, example="https://example.com/img.png")

class MainCategoryCreate(MainCategoryBase):
    pass

class MainCategoryUpdate(BaseModel):
    name: Optional[str] = None
    interval_minutes: Optional[int] = None
    image_url: Optional[str] = None

class MainCategoryOut(BaseModel):
    id: int
    name: str
    interval_minutes: int
    image_url: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
