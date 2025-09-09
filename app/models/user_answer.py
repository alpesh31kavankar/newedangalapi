# app/models/user_answer.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from app.database import Base

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    __table_args__ = (UniqueConstraint('unlock_id', 'user_id'),)

    answer_id = Column(Integer, primary_key=True, index=True)
    unlock_id = Column(Integer, ForeignKey("question_unlocks.unlock_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    chosen_product_id = Column(Integer, ForeignKey("products.product_id"))
    answered_at = Column(DateTime, server_default=func.now())
