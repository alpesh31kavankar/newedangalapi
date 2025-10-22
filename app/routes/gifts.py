from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/gifts",
    tags=["Gifts"]
)

# ---------------- Create gift ----------------
@router.post("/", response_model=schemas.gift.GiftOut)
def create_gift(gift: schemas.gift.GiftCreate, db: Session = Depends(get_db)):
    new_gift = models.gift.Gift(**gift.dict())
    db.add(new_gift)
    db.commit()
    db.refresh(new_gift)
    return new_gift

@router.get("/active", response_model=schemas.gift.GiftOut)
def get_active_gift(db: Session = Depends(get_db)):
    gift = db.query(models.gift.Gift).filter(models.gift.Gift.status == 'active').first()
    if not gift:
        raise HTTPException(status_code=404, detail="No active gift found")
    return gift

# ---------------- Get all gifts ----------------
@router.get("/", response_model=List[schemas.gift.GiftOut])
def get_gifts(db: Session = Depends(get_db)):
    return db.query(models.gift.Gift).all()


# ---------------- Get single gift by ID ----------------
@router.get("/{gift_id}", response_model=schemas.gift.GiftOut)
def get_gift(gift_id: int, db: Session = Depends(get_db)):
    gift = db.query(models.gift.Gift).filter(models.gift.Gift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    return gift


# ---------------- Update gift ----------------
@router.put("/{gift_id}", response_model=schemas.gift.GiftOut)
def update_gift(gift_id: int, update: schemas.gift.GiftUpdate, db: Session = Depends(get_db)):
    gift = db.query(models.gift.Gift).filter(models.gift.Gift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(gift, key, value)

    db.commit()
    db.refresh(gift)
    return gift


# ---------------- Delete gift ----------------
@router.delete("/{gift_id}")
def delete_gift(gift_id: int, db: Session = Depends(get_db)):
    gift = db.query(models.gift.Gift).filter(models.gift.Gift.id == gift_id).first()
    if not gift:
        raise HTTPException(status_code=404, detail="Gift not found")

    db.delete(gift)
    db.commit()
    return {"detail": "Gift deleted successfully"}
