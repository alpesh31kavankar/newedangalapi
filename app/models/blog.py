from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(BigInteger, primary_key=True, index=True)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)

    title = Column(Text, nullable=False)
    slug = Column(Text, unique=True, nullable=False)

    summary = Column(Text)
    content = Column(Text, nullable=False)

    winner_name = Column(Text)
    winner_margin = Column(Numeric)

    image_url = Column(Text)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    is_published = Column(Boolean, default=True)