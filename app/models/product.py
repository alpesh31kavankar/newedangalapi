
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
    manufacturer = Column(Text, nullable=False, default='')
    specifications = Column(Text, nullable=False, default='')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

