from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/user-categories", tags=["UserCategories"])

@router.post("/", response_model=schemas.user_category.UserCategoryOut)
def create_user_category(user_category: schemas.user_category.UserCategoryCreate, db: Session = Depends(get_db)):
    db_obj = models.user_category.UserCategory(**user_category.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[schemas.user_category.UserCategoryOut])
def get_user_categories(db: Session = Depends(get_db)):
    return db.query(models.user_category.UserCategory).all()
