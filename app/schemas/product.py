# app/schemas/product.py
from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    product_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    product_id: int

    class Config:
        orm_mode = True
