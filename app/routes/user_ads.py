from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/user-ads", tags=["User Ads"])

@router.post("/", response_model=schemas.user_ads.UserAdOut)
def watch_ad(user_ad: schemas.user_ads.UserAdCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    if user_ad.next_available_at and user_ad.next_available_at > now:
        raise HTTPException(status_code=400, detail="Ad not yet available for this user")
    
    db_ad = models.user_ads.UserAds(
        user_id=user_ad.user_id,
        next_available_at=now + timedelta(minutes=30),  # example cooldown 30min
        rewarded_token=user_ad.rewarded_token
    )
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@router.get("/", response_model=List[schemas.user_ads.UserAdOut])
def get_user_ads(db: Session = Depends(get_db)):
    return db.query(models.user_ads.UserAds).all()
