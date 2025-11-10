from sqlalchemy import Column, BigInteger, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class ProductSurveyQuestion(Base):
    __tablename__ = "product_sur_que"

    id = Column(BigInteger, primary_key=True, index=True)
    survey_question = Column(Text, nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    status = Column(Text, nullable=False, default="active")
    yes_count = Column(Integer, nullable=False, default=0)
    no_count = Column(Integer, nullable=False, default=0)
    maybe_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
