from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema
class ProductSurveyResponseBase(BaseModel):
    product_sur_queid: int
    userid: int
    response: str
    status: Optional[str] = "active"
    product_sur_resp_status: Optional[str] = "pending"


# Schema for creating
class ProductSurveyResponseCreate(ProductSurveyResponseBase):
    pass


# Schema for updating
class ProductSurveyResponseUpdate(BaseModel):
    product_sur_queid: Optional[int] = None
    userid: Optional[int] = None
    response: Optional[str] = None
    status: Optional[str] = None
    product_sur_resp_status: Optional[str] = None


# Schema for output
class ProductSurveyResponseOut(ProductSurveyResponseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
