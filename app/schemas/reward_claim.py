from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RewardClaimRequest(BaseModel):
    user_id: int
    lottery_id: int
    gift_id: int
    postal_code: str
    contact_no: str
    address: str
    claim_type: str = "winning"  # default

class RewardClaimResponse(BaseModel):
    message: str

class MyGiftResponse(BaseModel):
    claim_id: int
    claim_type: str
    is_claimed: bool
    lottery_id: int
    lottery_name: Optional[str]
    gift_name: Optional[str]
    gift_image: Optional[str]
    claimed_at: datetime

    class Config:
        orm_mode = True