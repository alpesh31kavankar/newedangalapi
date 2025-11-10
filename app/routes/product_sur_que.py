from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.product_sur_que import ProductSurveyQuestion
from ..schemas.product_sur_que import (
    ProductSurveyQuestionCreate,
    ProductSurveyQuestionUpdate,
    ProductSurveyQuestionOut,
)

router = APIRouter(prefix="/product-survey", tags=["Product Survey"])

# Create
@router.post("/", response_model=ProductSurveyQuestionOut)
def create_survey_question(data: ProductSurveyQuestionCreate, db: Session = Depends(get_db)):
    new_question = ProductSurveyQuestion(**data.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

# Read all
@router.get("/", response_model=list[ProductSurveyQuestionOut])
def get_all_survey_questions(db: Session = Depends(get_db)):
    return db.query(ProductSurveyQuestion).all()

# Read single
@router.get("/{id}", response_model=ProductSurveyQuestionOut)
def get_survey_question(id: int, db: Session = Depends(get_db)):
    question = db.query(ProductSurveyQuestion).filter(ProductSurveyQuestion.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Survey question not found")
    return question

# Update
@router.put("/{id}", response_model=ProductSurveyQuestionOut)
def update_survey_question(id: int, data: ProductSurveyQuestionUpdate, db: Session = Depends(get_db)):
    question = db.query(ProductSurveyQuestion).filter(ProductSurveyQuestion.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Survey question not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question

# Delete
@router.delete("/{id}")
def delete_survey_question(id: int, db: Session = Depends(get_db)):
    question = db.query(ProductSurveyQuestion).filter(ProductSurveyQuestion.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Survey question not found")

    db.delete(question)
    db.commit()
    return {"detail": "Survey question deleted successfully"}

@router.get("/by-product/{product_id}", response_model=ProductSurveyQuestionOut)
def get_question_by_product(product_id: int, db: Session = Depends(get_db)):
    question = db.query(ProductSurveyQuestion).filter(
        ProductSurveyQuestion.product_id == product_id,
        ProductSurveyQuestion.status == "active"
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="No active survey question for this product")
    return question


