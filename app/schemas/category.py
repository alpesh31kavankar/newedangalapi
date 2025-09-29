# from pydantic import BaseModel
# from typing import Optional

# # Shared base (no id here)
# class CategoryBase(BaseModel):
#     category_name: str
#     description: Optional[str] = None
#     icon_url: Optional[str] = None
#     image_url: Optional[str] = None

# # Schema for creating a new category (POST)
# class CategoryCreate(CategoryBase):
#     pass

# # Schema for updating a category (PUT)
# class CategoryUpdate(CategoryBase):
#     pass

# # Schema for returning data (GET), includes the ID
# class CategoryOut(CategoryBase):
#     category_id: int

#     class Config:
#         orm_mode = True

# schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime  # ✅ import this

class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str]
    image_url: Optional[str]
    round_interval_minutes: int = 30 

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    created_at: datetime  # ✅ use datetime
    updated_at: datetime  # ✅ use datetime

    class Config:
        orm_mode = True
