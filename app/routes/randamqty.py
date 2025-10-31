from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.randamqty import RandamQty
from ..schemas.randamqty import RandamQtyCreate, RandamQtyOut, RandamQtyUpdate

router = APIRouter(
    prefix="/randamqty",
    tags=["RandamQty"]
)

# Create a RandamQty
@router.post("/", response_model=RandamQtyOut)
def create_randamqty(randamqty: RandamQtyCreate, db: Session = Depends(get_db)):
    new_randamqty = RandamQty(**randamqty.dict())
    db.add(new_randamqty)
    db.commit()
    db.refresh(new_randamqty)
    return new_randamqty

# Get all RandamQty
@router.get("/", response_model=List[RandamQtyOut])
def get_all_randamqty(db: Session = Depends(get_db)):
    return db.query(RandamQty).all()

# Get single RandamQty by ID
@router.get("/{randamqty_id}", response_model=RandamQtyOut)
def get_randamqty(randamqty_id: int, db: Session = Depends(get_db)):
    item = db.query(RandamQty).filter(RandamQty.id == randamqty_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="RandamQty not found")
    return item

# Update RandamQty
@router.put("/{randamqty_id}", response_model=RandamQtyOut)
def update_randamqty(randamqty_id: int, updated_data: RandamQtyUpdate, db: Session = Depends(get_db)):
    item = db.query(RandamQty).filter(RandamQty.id == randamqty_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="RandamQty not found")
    
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item

# Delete RandamQty
@router.delete("/{randamqty_id}")
def delete_randamqty(randamqty_id: int, db: Session = Depends(get_db)):
    item = db.query(RandamQty).filter(RandamQty.id == randamqty_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="RandamQty not found")
    
    db.delete(item)
    db.commit()
    return {"detail": "RandamQty deleted successfully"}
