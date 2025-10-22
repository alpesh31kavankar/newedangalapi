from sqlalchemy import Column, BigInteger, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class Gift(Base):
    __tablename__ = "gifts"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Integer, nullable=False, default=0)
    status = Column(Text, nullable=False, default='inactive')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

  # Use string for relationship to avoid circular import
    lotteries = relationship("Lottery", back_populates="gift", lazy='select')