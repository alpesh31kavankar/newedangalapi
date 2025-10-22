from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.models.p_gift import PGift

router = APIRouter(
    prefix="/p_gifts",
    tags=["participant Gifts"]
)

# Create winner gift
@router.post("/", response_model=schemas.p_gift.PGiftOut)
def create_p_gift(gift: schemas.p_gift.PGiftCreate, db: Session = Depends(get_db)):
    new_gift = PGift(**gift.dict())
    db.add(new_gift)
    db.commit()
    db.refresh(new_gift)
    return new_gift

# Get all winner gifts
@router.get("/", response_model=List[schemas.p_gift.PGiftOut])
def get_p_gifts(db: Session = Depends(get_db)):
    return db.query(PGift).all()

# Get today's active winner gift
@router.get("/active", response_model=schemas.p_gift.PGiftOut)
def get_active_p_gift(db: Session = Depends(get_db)):
    gift = db.query(PGift).filter(PGift.status == 'active').first()
    if not gift:
        raise HTTPException(status_code=404, detail="No active paricipant gift found")
    return gift

# Update winner gift
@router.put("/{gift_id}", response_model=schemas.p_gift.PGiftOut)
def update_p_gift(gift_id: int, update: schemas.p_gift.PGiftUpdate, db: Session = Depends(get_db)):
    gift = db.query(PGift).filter(PGift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(gift, key, value)
    db.commit()
    db.refresh(gift)
    return gift

# Delete winner gift
@router.delete("/{gift_id}")
def delete_p_gift(gift_id: int, db: Session = Depends(get_db)):
    gift = db.query(PGift).filter(PGift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    db.delete(gift)
    db.commit()
    return {"detail": "participant gift deleted successfully"}
