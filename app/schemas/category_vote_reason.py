from pydantic import BaseModel
from typing import Optional


class CategoryVoteReasonBase(BaseModel):
    categories_id: int
    reason_key: str
    reason_label: str


class CategoryVoteReasonCreate(CategoryVoteReasonBase):
    pass


class CategoryVoteReasonOut(CategoryVoteReasonBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
