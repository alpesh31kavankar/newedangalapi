from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReviewBase(BaseModel):
    user_id: int
    product_id: int
    rating: int
    review_text: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
