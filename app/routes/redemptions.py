from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/redemptions", tags=["Redemptions"])

@router.post("/", response_model=schemas.redemptions.RedemptionOut)
def create_redemption(redemption: schemas.redemptions.RedemptionCreate, db: Session = Depends(get_db)):
    db_redemption = models.redemptions.Redemptions(**redemption.dict())
    db.add(db_redemption)
    db.commit()
    db.refresh(db_redemption)
    return db_redemption

@router.get("/", response_model=List[schemas.redemptions.RedemptionOut])
def get_redemptions(db: Session = Depends(get_db)):
    return db.query(models.redemptions.Redemptions).all()

@router.get("/{redemption_id}", response_model=schemas.redemptions.RedemptionOut)
def get_redemption(redemption_id: int, db: Session = Depends(get_db)):
    redemption = db.query(models.redemptions.Redemptions).filter(models.redemptions.Redemptions.redemption_id == redemption_id).first()
    if not redemption:
        raise HTTPException(status_code=404, detail="Redemption not found")
    return redemption
