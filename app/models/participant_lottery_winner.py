from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from ..database import Base
from .participant_lottery import ParticipantLottery

class ParticipantLotteryWinner(Base):
    __tablename__ = "participant_lottery_winner"

    id = Column(BigInteger, primary_key=True)
    lottery_id = Column(BigInteger, ForeignKey("participant_lotteries.id"))
    users_id = Column(BigInteger, nullable=False)
    token_id = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('now()'))

    lottery = relationship("ParticipantLottery")
