from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RedemptionBase(BaseModel):
    user_id: int
    draw_id: int
    product_id: int
    address: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = "pending"  # pending, shipped, delivered

class RedemptionCreate(RedemptionBase):
    pass

class RedemptionOut(RedemptionBase):
    redemption_id: int
    redeemed_at: datetime

    class Config:
        orm_mode = True
