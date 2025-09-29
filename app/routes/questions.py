# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# from app import models, schemas
# from app.database import get_db

# router = APIRouter(
#     prefix="/questions",
#     tags=["Questions"]
# )

# @router.post("/", response_model=schemas.question.QuestionOut)
# def create_question(question: schemas.question.QuestionCreate, db: Session = Depends(get_db)):
#     new_question = models.question.Question(**question.dict())
#     db.add(new_question)
#     db.commit()
#     db.refresh(new_question)
#     return new_question

# @router.get("/", response_model=List[schemas.question.QuestionOut])
# def get_questions(db: Session = Depends(get_db)):
#     return db.query(models.question.Question).all()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.question import Question
from ..schemas.question import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])

# Create a question
@router.post("/", response_model=QuestionOut)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    new_question = Question(**question.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

# Get all questions
@router.get("/", response_model=list[QuestionOut])
def get_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()

# Get single question
@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

