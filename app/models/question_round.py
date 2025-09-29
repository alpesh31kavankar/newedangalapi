from sqlalchemy import Column, BigInteger, ForeignKey, TIMESTAMP, Boolean, Integer
from sqlalchemy.sql import func
from ..database import Base

class QuestionRound(Base):
    __tablename__ = "question_rounds"

    id = Column(BigInteger, primary_key=True, index=True)
    questions_id = Column(BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    categories_id = Column(BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    product1_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    product2_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    release_time = Column(TIMESTAMP(timezone=True), nullable=False)
    max_votes = Column(Integer, nullable=False)
    is_locked = Column(Boolean, default=False)
    votes_product1 = Column(Integer, default=0)
    votes_product2 = Column(Integer, default=0)
    winner_product_id = Column(BigInteger, ForeignKey("products.id"), nullable=True)
    is_draw = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
