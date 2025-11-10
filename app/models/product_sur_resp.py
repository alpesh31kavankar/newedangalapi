from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class ProductSurveyResponse(Base):
    __tablename__ = "product_sur_resp"

    id = Column(BigInteger, primary_key=True, index=True)
    product_sur_queid = Column(BigInteger, ForeignKey("product_sur_que.id", ondelete="CASCADE"), nullable=False)
    userid = Column(BigInteger, nullable=False)
    response = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="active")
    product_sur_resp_status = Column(Text, nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
