from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlogBase(BaseModel):
    category_id: int
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    winner_name: Optional[str] = None
    winner_margin: Optional[float] = None
    image_url: Optional[str] = None
    is_published: bool = True


class BlogCreate(BlogBase):
    pass


class BlogResponse(BlogBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True