from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class DailyQuestionAnswer(Base):
    __tablename__ = "daily_question_answer"

    id = Column(BigInteger, primary_key=True, index=True)
    daily_question_id = Column(BigInteger, ForeignKey("daily_question.id"), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    answer = Column(String(10), nullable=False)  # 'Yes' or 'No'

    daily_question = relationship("DailyQuestion", back_populates="answers")
