from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

@router.post("/", response_model=schemas.question.QuestionOut)
def create_question(question: schemas.question.QuestionCreate, db: Session = Depends(get_db)):
    new_question = models.question.Question(**question.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.get("/", response_model=List[schemas.question.QuestionOut])
def get_questions(db: Session = Depends(get_db)):
    return db.query(models.question.Question).all()
