from sqlalchemy import Column, BigInteger, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class DailyQuestion(Base):
    __tablename__ = "daily_question"

    id = Column(BigInteger, primary_key=True, index=True)
    randamqty_id = Column(BigInteger, ForeignKey("randamqty.id"), nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    randamqty = relationship("RandamQty")
    answers = relationship("DailyQuestionAnswer", back_populates="daily_question")
