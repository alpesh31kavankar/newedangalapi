# app/schemas/category.py
from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    category_id: int

    class Config:
        orm_mode = True
