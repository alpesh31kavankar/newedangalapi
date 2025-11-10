from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema
class ProductSurveyQuestionBase(BaseModel):
    survey_question: str
    product_id: int
    status: Optional[str] = "active"
    yes_count: Optional[int] = 0
    no_count: Optional[int] = 0
    maybe_count: Optional[int] = 0

# Schema for creating
class ProductSurveyQuestionCreate(ProductSurveyQuestionBase):
    pass

# Schema for updating
class ProductSurveyQuestionUpdate(BaseModel):
    survey_question: Optional[str] = None
    product_id: Optional[int] = None
    status: Optional[str] = None
    yes_count: Optional[int] = None
    no_count: Optional[int] = None
    maybe_count: Optional[int] = None

# Schema for output
class ProductSurveyQuestionOut(ProductSurveyQuestionBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
