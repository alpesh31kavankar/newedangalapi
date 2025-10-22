from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    categories_id: int
    name: str
    details: Optional[str] = None
    nationality: Optional[str] = None
    image_url: Optional[str] = None
    manufacturer: Optional[str] = ""       # 👈 added
    specifications: Optional[str] = ""     # 👈 added

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    avg_rating: float = 0                   # 👈 new
    review_count: int = 0                   # 👈 new

    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)
