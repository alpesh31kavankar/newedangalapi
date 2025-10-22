from sqlalchemy import Column, BigInteger, Integer, Boolean, ForeignKey, Date, TIMESTAMP, text
from sqlalchemy.orm import relationship
from ..database import Base
from .gift import Gift

class Lottery(Base):
    __tablename__ = "lotteries"

    id = Column(BigInteger, primary_key=True)
    lottery_date = Column(Date, nullable=False)
    lottery_round = Column(Integer, default=1)
    gifts_id = Column(BigInteger, ForeignKey("gifts.id"))
    is_completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text('now()'))
    updated_at = Column(TIMESTAMP, server_default=text('now()'))

    gift = relationship("Gift", back_populates="lotteries")

