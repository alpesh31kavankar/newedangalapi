from sqlalchemy import Column, BigInteger, Date, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class DailyTicketClaim(Base):
    __tablename__ = "daily_ticket_claims"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reward_id = Column(BigInteger, ForeignKey("ticket_rewards.id", ondelete="CASCADE"), nullable=False)
    collected_date = Column(Date, nullable=False, server_default=func.current_date())
    collected_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Add this relationship
    reward = relationship("TicketReward", backref="claims")

    __table_args__ = (
        UniqueConstraint("user_id", "reward_id", name="uix_user_reward"),
    )
