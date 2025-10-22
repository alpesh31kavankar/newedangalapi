from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from ..database import Base
from .lottery import Lottery

class LotteryWinner(Base):
    __tablename__ = "lottery_winner"

    id = Column(BigInteger, primary_key=True)
    lotteries_id = Column(BigInteger, ForeignKey("lotteries.id"))
    users_id = Column(BigInteger, nullable=False)
    token_id = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('now()'))

    lottery = relationship("Lottery")
