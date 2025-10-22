# app/schemas/email_verification.py
from pydantic import BaseModel
from datetime import datetime

class EmailVerificationBase(BaseModel):
    users_id: int
    token: str
    expires_at: datetime
    is_used: bool

    class Config:
        orm_mode = True

class EmailVerificationOut(EmailVerificationBase):
    id: int
    created_at: datetime
    updated_at: datetime
