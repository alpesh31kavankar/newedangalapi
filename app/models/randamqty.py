from sqlalchemy import Column, BigInteger, Text, String, TIMESTAMP
from sqlalchemy.sql import func
from ..database import Base

class RandamQty(Base):
    __tablename__ = "randamqty"

    id = Column(BigInteger, primary_key=True, index=True)
    randamqty_text = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="Active")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
