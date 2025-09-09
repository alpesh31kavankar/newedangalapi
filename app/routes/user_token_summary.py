from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/user-token-summaries",
    tags=["UserTokenSummary"]
)

@router.post("/", response_model=schemas.user_token_summary.UserTokenSummaryOut)
def create_summary(summary: schemas.user_token_summary.UserTokenSummaryCreate, db: Session = Depends(get_db)):
    db_summary = models.user_token_summary.UserTokenSummary(**summary.dict())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

@router.get("/", response_model=List[schemas.user_token_summary.UserTokenSummaryOut])
def get_summaries(db: Session = Depends(get_db)):
    return db.query(models.user_token_summary.UserTokenSummary).all()

@router.get("/{summary_id}", response_model=schemas.user_token_summary.UserTokenSummaryOut)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(models.user_token_summary.UserTokenSummary).filter(models.user_token_summary.UserTokenSummary.summary_id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.put("/{summary_id}", response_model=schemas.user_token_summary.UserTokenSummaryOut)
def update_summary(summary_id: int, update: schemas.user_token_summary.UserTokenSummaryUpdate, db: Session = Depends(get_db)):
    summary = db.query(models.user_token_summary.UserTokenSummary).filter(models.user_token_summary.UserTokenSummary.summary_id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(summary, key, value)

    db.commit()
    db.refresh(summary)
    return summary

@router.delete("/{summary_id}")
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(models.user_token_summary.UserTokenSummary).filter(models.user_token_summary.UserTokenSummary.summary_id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    db.delete(summary)
    db.commit()
    return {"detail": "Summary deleted successfully"}
