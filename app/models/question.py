# from sqlalchemy import Column, Integer, Text
# from app.database import Base

# class Question(Base):
#     __tablename__ = "questionbank"

#     question_id = Column(Integer, primary_key=True, index=True)
#     question_text = Column(Text, nullable=False)

from sqlalchemy import Column, BigInteger, Text, TIMESTAMP
from sqlalchemy.sql import func
from ..database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

