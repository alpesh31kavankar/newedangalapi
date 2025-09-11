from pydantic import BaseModel
from typing import Optional

# Shared base (no id here)
class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None

# Schema for creating a new category (POST)
class CategoryCreate(CategoryBase):
    pass

# Schema for updating a category (PUT)
class CategoryUpdate(CategoryBase):
    pass

# Schema for returning data (GET), includes the ID
class CategoryOut(CategoryBase):
    category_id: int

    class Config:
        orm_mode = True
