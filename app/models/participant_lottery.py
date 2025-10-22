from sqlalchemy import Column, BigInteger, Integer, Boolean, ForeignKey, Date, TIMESTAMP, text
from sqlalchemy.orm import relationship
from ..database import Base
from .p_gift import PGift

class ParticipantLottery(Base):
    __tablename__ = "participant_lotteries"

    id = Column(BigInteger, primary_key=True)
    lottery_date = Column(Date, nullable=False)
    lottery_round = Column(Integer, default=1)
    p_gifts_id = Column(BigInteger, ForeignKey("p_gifts.id"))
    is_completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text('now()'))
    updated_at = Column(TIMESTAMP, server_default=text('now()'))

    p_gift = relationship("PGift", back_populates="participant_lotteries")
