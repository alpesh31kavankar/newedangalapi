from sqlalchemy import Column, Integer, Text
from app.database import Base

class Question(Base):
    __tablename__ = "questionbank"

    question_id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
