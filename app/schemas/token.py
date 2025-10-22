from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

class TokenOut(BaseModel):
    tokens_id: str = Field(..., alias="token_id") 
    users_id: int
    question_rounds_id: Optional[int]
    product_id: Optional[int]
    token_type: str
    source: str
    created_at: datetime

    class Config:
        orm_mode = True
