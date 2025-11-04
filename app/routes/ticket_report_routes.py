from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.ticket_report import TicketReport
from ..schemas.ticket_report_schema import TicketReportCreate, TicketReportResponse
from typing import List

router = APIRouter(prefix="/reports", tags=["Ticket Reports"])

@router.post("/", response_model=TicketReportResponse)
def create_ticket_report(report: TicketReportCreate, db: Session = Depends(get_db)):
    new_report = TicketReport(
        ticket_no=report.ticket_no,
        user_id=report.user_id,
        report_reason=report.report_reason,
        report_details=report.report_details,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/", response_model=List[TicketReportResponse])
def get_all_reports(db: Session = Depends(get_db)):
    return db.query(TicketReport).order_by(TicketReport.created_at.desc()).all()
