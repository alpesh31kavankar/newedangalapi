from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema (common fields)
class RandamQtyBase(BaseModel):
    randamqty_text: str
    status: Optional[str] = "Active"

# Create schema
class RandamQtyCreate(RandamQtyBase):
    pass

# Update schema
class RandamQtyUpdate(BaseModel):
    randamqty_text: Optional[str] = None
    status: Optional[str] = None

# Output schema
class RandamQtyOut(RandamQtyBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
