from sqlalchemy import Column, BigInteger, Integer, Time, Boolean
from app.database import Base

class TicketReward(Base):
    __tablename__ = "ticket_rewards"
    id = Column(BigInteger, primary_key=True)
    day_number = Column(Integer, unique=True, nullable=False)
    tickets = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False, default="00:00")
    end_time = Column(Time, nullable=False, default="20:00")
    active = Column(Boolean, default=True)
