from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/user-answers", tags=["UserAnswers"])

@router.post("/", response_model=schemas.user_answer.UserAnswerOut)
def create_user_answer(answer: schemas.user_answer.UserAnswerCreate, db: Session = Depends(get_db)):
    db_answer = models.user_answer.UserAnswer(**answer.dict())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

@router.get("/", response_model=List[schemas.user_answer.UserAnswerOut])
def get_user_answers(db: Session = Depends(get_db)):
    return db.query(models.user_answer.UserAnswer).all()
