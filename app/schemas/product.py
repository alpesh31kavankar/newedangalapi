# # app/schemas/product.py
# from pydantic import BaseModel
# from typing import Optional

# class ProductBase(BaseModel):
#     product_name: str
#     description: Optional[str] = None
#     image_url: Optional[str] = None
#     category_id: Optional[int] = None

# class ProductCreate(ProductBase):
#     pass

# class ProductUpdate(ProductBase):
#     pass

# class ProductOut(ProductBase):
#     product_id: int

#     class Config:
#         orm_mode = True

from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    categories_id: int
    name: str
    details: Optional[str]
    nationality: Optional[str]
    image_url: Optional[str]

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

