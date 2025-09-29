from sqlalchemy import Column, BigInteger, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from ..database import Base

class Vote(Base):
    __tablename__ = "votes"

    id = Column(BigInteger, primary_key=True, index=True)
    users_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_rounds_id = Column(BigInteger, ForeignKey("question_rounds.id", ondelete="CASCADE"), nullable=False)
    products_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('users_id', 'question_rounds_id', name='uq_user_round'),
    )
