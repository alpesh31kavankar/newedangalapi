from pydantic import BaseModel
from datetime import datetime

class UserCategoryBase(BaseModel):
    user_id: int
    category_id: int

class UserCategoryCreate(UserCategoryBase):
    pass

class UserCategoryOut(UserCategoryBase):
    user_category_id: int
    selected_at: datetime

    class Config:
        orm_mode = True
