# app/models/question_unlock.py
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from app.database import Base

class QuestionUnlock(Base):
    __tablename__ = 'question_unlocks'
    __table_args__ = (UniqueConstraint('draw_id', 'question_id', 'product1_id', 'product2_id'),)

    unlock_id = Column(Integer, primary_key=True, index=True)
    draw_id = Column(Integer, ForeignKey("draws.draw_id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questionbank.question_id", ondelete="CASCADE"))
    product1_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))
    product2_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))
    unlock_time = Column(DateTime, nullable=False)
    cutoff_time = Column(DateTime, nullable=False)
    current_users = Column(Integer, default=0)
    max_users = Column(Integer, default=100)
    is_closed = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    winning_product_id = Column(Integer, ForeignKey("products.product_id"))
