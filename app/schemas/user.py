# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime

# class UserBase(BaseModel):
#     username: str
#     email: EmailStr
#     full_name: Optional[str] = None
#     phone_number: Optional[str] = None
#     address: Optional[str] = None

# class UserCreate(UserBase):
#     password: str

# class UserResponse(UserBase):
#     user_id: int
#     created_at: datetime

#     class Config:
#         orm_mode = True

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# Shared fields
class UserBase(BaseModel):
    username: str
    email: EmailStr
    gender: Optional[str]
    birth_date: date
    pincode: str
    referral_code: Optional[str]
    referred_by: Optional[str]
    mobile_no: Optional[str]
    profile_image: Optional[str]
    address: Optional[str]

# Fields required for creation
class UserCreate(UserBase):
    password: str

# Fields returned via API
class UserOut(UserBase):
    id: int
    is_verified: bool
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
