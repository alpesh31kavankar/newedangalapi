from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketReportCreate(BaseModel):
    ticket_no: str
    user_id: int
    report_reason: str
    report_details: Optional[str] = None

class TicketReportResponse(BaseModel):
    id: int
    ticket_no: str
    user_id: int
    report_reason: str
    report_details: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
