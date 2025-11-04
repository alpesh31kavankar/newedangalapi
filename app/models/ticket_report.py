from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, func
from ..database import Base

class TicketReport(Base):
    __tablename__ = "ticket_reports"

    id = Column(BigInteger, primary_key=True, index=True)
    ticket_no = Column(String(50), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    report_reason = Column(String(255), nullable=False)
    report_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
