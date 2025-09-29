# # app/models/product.py
# from sqlalchemy import Column, Integer, String, Text, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base

# class Product(Base):
#     __tablename__ = "products"

#     product_id = Column(Integer, primary_key=True, index=True)
#     product_name = Column(String(200), nullable=False, index=True)
#     description = Column(Text, nullable=True)
#     image_url = Column(Text, nullable=True)
#     category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)

#     # Relationship (optional, for easy joins)
#     category = relationship("Category", backref="products")

from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    categories_id = Column(BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    nationality = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

