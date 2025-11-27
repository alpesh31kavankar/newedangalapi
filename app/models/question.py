
from sqlalchemy import Column, BigInteger, Text, TIMESTAMP,ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

