from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/draws",
    tags=["Draws"]
)

@router.post("/", response_model=schemas.draw.DrawOut)
def create_draw(draw: schemas.draw.DrawCreate, db: Session = Depends(get_db)):
    new_draw = models.draw.Draw(**draw.dict())
    db.add(new_draw)
    db.commit()
    db.refresh(new_draw)
    return new_draw

@router.get("/", response_model=List[schemas.draw.DrawOut])
def get_draws(db: Session = Depends(get_db)):
    return db.query(models.draw.Draw).all()
