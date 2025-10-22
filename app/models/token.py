from sqlalchemy import Column, BigInteger, ForeignKey, Text, String, TIMESTAMP
from sqlalchemy.sql import func
from ..database import Base

class Token(Base):
    __tablename__ = "tokens"

    token_id = Column(Text, primary_key=True, index=True)
    users_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_rounds_id = Column(BigInteger, ForeignKey("question_rounds.id"), nullable=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=True)
    token_type = Column(String(20), nullable=False)  # 'participation' or 'winning'
    source = Column(String(50), default="system")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
