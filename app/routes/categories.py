# app/routers/category.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# Create category
@router.post("/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.category.Category).filter(models.category.Category.category_name == category.category_name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = models.category.Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# Get all categories
# @router.get("/", response_model=List[CategoryOut])
# def get_categories(db: Session = Depends(get_db)):
#     return db.query(models.category.Category).all()
#     #  return [{"category_id": 1, "category_name": "Mock"}]

@router.get("/", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.category.Category).all()

# Get single category
@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.category.Category).filter(models.category.Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Update category
@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, update: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(models.category.Category).filter(models.category.Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

# Delete category
@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.category.Category).filter(models.category.Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": "Category deleted successfully"}
