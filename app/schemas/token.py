from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TokenOut(BaseModel):
    tokens_id: str
    users_id: int
    question_rounds_id: Optional[int]
    product_id: Optional[int]
    token_type: str
    source: str
    created_at: datetime

    class Config:
        orm_mode = True
