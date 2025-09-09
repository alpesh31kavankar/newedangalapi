from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/question-unlocks", tags=["QuestionUnlocks"])

@router.post("/", response_model=schemas.question_unlock.QuestionUnlockOut)
def create_question_unlock(data: schemas.question_unlock.QuestionUnlockCreate, db: Session = Depends(get_db)):
    db_obj = models.question_unlock.QuestionUnlock(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[schemas.question_unlock.QuestionUnlockOut])
def get_question_unlocks(db: Session = Depends(get_db)):
    return db.query(models.question_unlock.QuestionUnlock).all()
