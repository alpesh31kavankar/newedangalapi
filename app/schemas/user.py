from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

# Shared fields
class UserBase(BaseModel):
    username: str
    email: EmailStr
    gender: Optional[str] = None
    birth_date: Optional[date] = None   # 👈 now optional
    pincode: Optional[str] = None     
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    mobile_no: Optional[str] = None       # 👈 default None
    profile_image: Optional[str] = None   # 👈 default None
    address: Optional[str] = None         # 👈 default None

# Fields required for creation
class UserCreate(UserBase):
    password: str

# Fields returned via API
class UserOut(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    activation_link: Optional[str] = None  # 👈 add here for testing

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    mobile_no: Optional[str] = None
    address: Optional[str] = None